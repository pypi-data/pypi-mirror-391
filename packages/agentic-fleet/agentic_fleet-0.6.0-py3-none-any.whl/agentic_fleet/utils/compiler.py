"""
DSPy compilation utilities for optimizing modules.
"""

from datetime import datetime
import hashlib
import inspect
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional

import dspy

from .gepa_optimizer import convert_to_dspy_examples
from .gepa_optimizer import harvest_history_examples
from .gepa_optimizer import optimize_with_gepa
from .gepa_optimizer import prepare_gepa_datasets


logger = logging.getLogger(__name__)

# Cache version for invalidation
CACHE_VERSION = 2  # Incremented to include signature/config hashes


def _compute_signature_hash() -> str:
    """
    Compute hash of all DSPy signature classes.

    This ensures cache invalidation when signatures change, following
    DSPy best practices for tracking signature modifications.

    Returns:
        SHA256 hash of signature source code
    """
    try:
        from ..dspy_modules import handoff_signatures  # type: ignore
        from ..dspy_modules import signatures

        # Collect all signature classes
        signature_classes = []

        # Get signatures from signatures.py
        for name, obj in inspect.getmembers(signatures):
            if inspect.isclass(obj) and issubclass(obj, dspy.Signature) and obj != dspy.Signature:
                signature_classes.append((name, inspect.getsource(obj)))

        # Get signatures from handoff_signatures.py
        for name, obj in inspect.getmembers(handoff_signatures):
            if inspect.isclass(obj) and issubclass(obj, dspy.Signature) and obj != dspy.Signature:
                signature_classes.append((name, inspect.getsource(obj)))

        # Sort for consistent hashing
        signature_classes.sort(key=lambda x: x[0])

        # Compute hash of all signature source code
        combined_source = "\n".join([f"{name}:\n{source}" for name, source in signature_classes])
        return hashlib.sha256(combined_source.encode()).hexdigest()[:16]
    except Exception as e:
        logger.warning(f"Failed to compute signature hash: {e}")
        return "unknown"


def _compute_config_hash(
    dspy_model: str,
    optimizer: str,
    gepa_options: Optional[Dict[str, Any]] = None,
    agent_config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Compute hash of configuration that affects compilation.

    Includes DSPy config (model, optimizer settings) and Agent Framework
    agent config (models, tools) since DSPy routing depends on agent capabilities.

    Args:
        dspy_model: DSPy model identifier
        optimizer: Optimization strategy
        gepa_options: GEPA optimizer options
        agent_config: Agent Framework agent configuration

    Returns:
        SHA256 hash of configuration
    """
    try:
        config_data = {
            "dspy_model": dspy_model,
            "optimizer": optimizer,
            "gepa_options": json.dumps(gepa_options or {}, sort_keys=True),
            "agent_config": json.dumps(agent_config or {}, sort_keys=True),
        }

        # Create deterministic JSON string
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    except Exception as e:
        logger.warning(f"Failed to compute config hash: {e}")
        return "unknown"


def _get_cache_metadata(cache_path: str) -> Optional[Dict[str, Any]]:
    """Get metadata from cache file if it exists.

    Args:
        cache_path: Path to cache file

    Returns:
        Dictionary with cache metadata or None
    """
    metadata_path = cache_path + ".meta"
    if not os.path.exists(metadata_path):
        return None

    try:
        with open(metadata_path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache_metadata(
    cache_path: str,
    examples_path: str,
    version: int = CACHE_VERSION,
    optimizer: str = "bootstrap",
    serializer: str = "pickle",
    signature_hash: Optional[str] = None,
    config_hash: Optional[str] = None,
):
    """Save cache metadata.

    Args:
        cache_path: Path to cache file
        examples_path: Path to examples file used for compilation
        version: Cache version number
        optimizer: Optimization strategy used
        serializer: Serialization method used
        signature_hash: Hash of signature classes (for granular invalidation)
        config_hash: Hash of configuration (for granular invalidation)
    """
    metadata_path = cache_path + ".meta"
    metadata = {
        "version": version,
        "examples_path": examples_path,
        "examples_mtime": os.path.getmtime(examples_path) if os.path.exists(examples_path) else 0,
        "optimizer": optimizer,
        "serializer": serializer,
        "created_at": datetime.now().isoformat(),
    }

    # Add signature and config hashes for granular invalidation
    if signature_hash:
        metadata["signature_hash"] = signature_hash
    if config_hash:
        metadata["config_hash"] = config_hash

    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save cache metadata: {e}")


def _is_cache_valid(
    cache_path: str,
    examples_path: str,
    optimizer: str,
    signature_hash: Optional[str] = None,
    config_hash: Optional[str] = None,
) -> bool:
    """Check if cache is valid based on modification times, version, and hashes.

    Args:
        cache_path: Path to cached compiled module
        examples_path: Path to training examples file
        optimizer: Optimization strategy
        signature_hash: Current signature hash (for granular invalidation)
        config_hash: Current config hash (for granular invalidation)

    Returns:
        True if cache exists and is valid, False otherwise
    """
    if not os.path.exists(cache_path) or not os.path.exists(examples_path):
        return False

    # Reject obviously invalid tiny cache artifacts (<64 bytes) early
    try:
        if os.path.getsize(cache_path) < 64:
            return False
    except OSError:
        return False

    # Check cache metadata version
    metadata = _get_cache_metadata(cache_path)
    if metadata:
        if metadata.get("version") != CACHE_VERSION:
            logger.debug(f"Cache version mismatch: {metadata.get('version')} != {CACHE_VERSION}")
            return False
        cached_optimizer = metadata.get("optimizer", "bootstrap")
        if cached_optimizer != optimizer:
            logger.debug("Cache optimizer mismatch: %s != %s", cached_optimizer, optimizer)
            return False
        serializer = metadata.get("serializer", "pickle")
        if serializer == "none":
            logger.debug("Cache marked with serializer 'none' – treating as invalid")
            return False

        # Check signature hash if available (granular invalidation)
        if signature_hash and "signature_hash" in metadata:
            if metadata["signature_hash"] != signature_hash:
                logger.debug(
                    "Cache signature hash mismatch: signatures changed, invalidating cache"
                )
                return False

        # Check config hash if available (granular invalidation)
        if config_hash and "config_hash" in metadata:
            if metadata["config_hash"] != config_hash:
                logger.debug(
                    "Cache config hash mismatch: configuration changed, invalidating cache"
                )
                return False

    try:
        cache_mtime = os.path.getmtime(cache_path)
        examples_mtime = os.path.getmtime(examples_path)

        # Cache is valid if it's newer than examples file
        if cache_mtime < examples_mtime:
            return False

        # Also check metadata if available
        if metadata:
            stored_mtime = metadata.get("examples_mtime", 0)
            if stored_mtime < examples_mtime:
                return False

        return True
    except OSError:
        # If we can't get mtime, assume cache is invalid
        return False


def _validate_example_alignment(records: List[Dict[str, Any]]) -> List[str]:
    """
    Validate that training examples match runtime call patterns.

    Checks that examples include required fields that match the forward() method
    signature and runtime usage patterns.

    Args:
        records: List of training example dictionaries

    Returns:
        List of validation warnings (empty if all valid)
    """
    warnings = []
    required_fields = ["task", "assigned_to", "mode"]
    optional_fields = [  # noqa: F841
        "team",
        "team_capabilities",
        "available_tools",
        "context",
        "tool_requirements",
    ]

    for i, record in enumerate(records):
        # Check required fields
        missing_required = [
            field for field in required_fields if field not in record or not record[field]
        ]
        if missing_required:
            warnings.append(f"Example {i}: Missing required fields: {', '.join(missing_required)}")

        # Check that mode is valid
        mode = record.get("mode", record.get("execution_mode", ""))
        if mode and mode not in ["delegated", "sequential", "parallel"]:
            warnings.append(
                f"Example {i}: Invalid execution mode '{mode}' (should be delegated/sequential/parallel)"
            )

        # Check that assigned_to matches team capabilities
        assigned = record.get("assigned_to", "")
        team = record.get("team", record.get("team_capabilities", ""))
        if assigned and team:
            # Basic check: assigned agent should be mentioned in team
            assigned_agents = [a.strip() for a in str(assigned).split(",")]
            for agent in assigned_agents:
                if agent and agent not in team:
                    warnings.append(
                        f"Example {i}: Assigned agent '{agent}' not found in team description"
                    )

    if warnings:
        logger.warning(f"Training example validation found {len(warnings)} issues:")
        for warning in warnings[:10]:  # Limit to first 10 warnings
            logger.warning(f"  - {warning}")
        if len(warnings) > 10:
            logger.warning(f"  ... and {len(warnings) - 10} more issues")

    return warnings


def compile_supervisor(
    module: Any,
    examples_path: str = "data/supervisor_examples.json",
    use_cache: bool = True,
    optimizer: str = "bootstrap",
    gepa_options: Optional[Dict[str, Any]] = None,
    dspy_model: Optional[str] = None,
    agent_config: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Compile DSPy supervisor module with training examples.

    Args:
        module: DSPy module to compile
        examples_path: Path to training examples JSON
        use_cache: Whether to use cached compiled module if available
        optimizer: Optimization strategy ("bootstrap" or "gepa")
        gepa_options: Additional options when using GEPA optimizer
        dspy_model: DSPy model identifier (for config hash)
        agent_config: Agent Framework agent configuration (for config hash)

    Returns:
        Compiled DSPy module
    """

    optimizer = optimizer or "bootstrap"
    cache_path = "logs/compiled_supervisor.pkl"

    # Compute hashes for granular cache invalidation
    signature_hash = _compute_signature_hash()
    config_hash = None
    if dspy_model:
        config_hash = _compute_config_hash(
            dspy_model=dspy_model,
            optimizer=optimizer,
            gepa_options=gepa_options,
            agent_config=agent_config,
        )

    if use_cache:
        if _is_cache_valid(
            cache_path,
            examples_path,
            optimizer,
            signature_hash=signature_hash,
            config_hash=config_hash,
        ):
            cached = load_compiled_module(cache_path)
            if cached is not None:
                logger.info("✓ Using cached compiled module from %s (%s)", cache_path, optimizer)
                return cached
        else:
            if os.path.exists(cache_path):
                logger.info("Cache invalidated for optimizer '%s'; recompiling...", optimizer)
            else:
                logger.debug("No cache found for optimizer '%s'; compiling...", optimizer)

    if not os.path.exists(examples_path):
        logger.warning(f"No training data found at {examples_path}, using uncompiled module")
        return module

    try:
        with open(examples_path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load training data from {examples_path}: {exc}")
        return module

    # Validate example alignment with runtime patterns
    if isinstance(data, list) and data:
        validation_warnings = _validate_example_alignment(data)
        if validation_warnings:
            logger.warning(
                f"Found {len(validation_warnings)} validation issues in training examples. "
                "Some examples may not align with runtime call patterns."
            )

    try:
        if optimizer == "gepa":
            gepa_options = gepa_options or {}
            extra_examples: List[Dict[str, Any]] = list(gepa_options.get("extra_examples", []))

            if gepa_options.get("use_history_examples"):
                history_examples = harvest_history_examples(
                    min_quality=gepa_options.get("history_min_quality", 8.0),
                    limit=gepa_options.get("history_limit", 200),
                )
                if history_examples:
                    extra_examples.extend(history_examples)
                    logger.info(
                        "Appended %d history-derived examples for GEPA",
                        len(history_examples),
                    )

            trainset, valset = prepare_gepa_datasets(
                base_examples_path=examples_path,
                base_records=data,
                extra_examples=extra_examples,
                val_split=gepa_options.get("val_split", 0.2),
                seed=gepa_options.get("seed", 13),
            )

            # Enforce exclusivity at compilation time to avoid silent misconfiguration
            auto_flag = gepa_options.get("auto")
            max_full_flag = gepa_options.get("max_full_evals")
            max_metric_flag = gepa_options.get("max_metric_calls")
            chosen_flags = [c for c in [auto_flag, max_full_flag, max_metric_flag] if c is not None]
            if len(chosen_flags) != 1:
                raise ValueError(
                    "Exactly one of max_metric_calls, max_full_evals, auto must be set. "
                    f"You set max_metric_calls={max_metric_flag}, max_full_evals={max_full_flag}, auto={auto_flag}."
                )

            # Log edge case examples being used for training
            edge_case_count = sum(
                1
                for ex in trainset + (list(valset) if valset else [])
                if hasattr(ex, "context") and "edge case" in str(ex.context).lower()
            )
            if edge_case_count > 0:
                logger.info(
                    f"GEPA training includes {edge_case_count} edge case examples for better routing"
                )

            compiled = optimize_with_gepa(
                module,
                trainset,
                valset,
                auto=auto_flag,
                max_full_evals=max_full_flag,
                max_metric_calls=max_metric_flag,
                reflection_model=gepa_options.get("reflection_model"),
                perfect_score=gepa_options.get("perfect_score", 1.0),
                log_dir=gepa_options.get("log_dir", "logs/gepa"),
            )

            # Log GEPA optimization completion with edge case awareness
            logger.info(
                f"✓ GEPA optimization complete: {len(trainset)} train, {
                    len(valset) if valset else 0
                } val examples. "
                f"Edge cases captured: {edge_case_count}. Check {
                    gepa_options.get('log_dir', 'logs/gepa')
                } for detailed feedback."
            )
        else:
            trainset = convert_to_dspy_examples(data)

            def routing_metric(example, prediction, trace=None):
                correct_assignment = example.assigned_to in prediction.assigned_to
                correct_mode = example.execution_mode == prediction.execution_mode
                tool_score = 1.0
                if hasattr(example, "tool_requirements") and example.tool_requirements:
                    tool_score = 1.0
                base_score = float(correct_assignment and correct_mode)
                return base_score * 0.8 + tool_score * 0.2

            from dspy.teleprompt import BootstrapFewShot

            max_demos = gepa_options.get("max_bootstrapped_demos", 4) if gepa_options else 4
            optimizer_instance = BootstrapFewShot(
                metric=routing_metric,
                max_bootstrapped_demos=max_demos,
                max_labeled_demos=max_demos,
            )

            compiled = optimizer_instance.compile(module, trainset=trainset)
            logger.info(f"✓ Module compiled with {len(trainset)} examples (bootstrap)")

        if use_cache:
            try:
                serializer_used = save_compiled_module(compiled, cache_path)
                _save_cache_metadata(
                    cache_path,
                    examples_path,
                    CACHE_VERSION,
                    optimizer,
                    serializer=serializer_used,
                    signature_hash=signature_hash,
                    config_hash=config_hash,
                )
            except Exception as e:
                # Ensure no partial artifact remains
                try:
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                        if os.path.exists(cache_path + ".meta"):
                            os.remove(cache_path + ".meta")
                except Exception:
                    pass
                logger.warning(
                    "Skipping cache metadata creation due to serialization failure; will compile fresh next run (%s)",
                    e,
                )

        return compiled

    except Exception as e:
        logger.error(f"Failed to compile module with {optimizer}: {e}")
        return module


def save_compiled_module(module: Any, filepath: str) -> str:
    """Save compiled DSPy module for reuse atomically.

    Writes to a temporary file and renames on success. Returns serializer used.
    Raises if both strategies fail, leaving no artifact behind.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    tmp_path = filepath + ".tmp"

    def _attempt_pickle() -> bool:
        try:
            import pickle

            with open(tmp_path, "wb") as f:
                pickle.dump(module, f)
            logger.info(f"Compiled module serialized (pickle) to temp path {tmp_path}")
            return True
        except Exception as e:
            logger.warning(f"Primary pickle serialization failed: {e}. Trying dill fallback...")
            return False

    def _attempt_dill() -> bool:
        try:
            import dill  # type: ignore

            with open(tmp_path, "wb") as f:
                dill.dump(module, f)  # type: ignore
            logger.info(f"Compiled module serialized (dill) to temp path {tmp_path}")
            return True
        except Exception as e:  # pragma: no cover
            logger.error(f"Failed to serialize compiled module with dill: {e}")
            return False

    # Remove any stale temp
    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except Exception:
        pass

    used = "pickle" if _attempt_pickle() else "dill" if _attempt_dill() else "none"
    if used == "none":
        # Cleanup temp file if present
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise RuntimeError("Failed to serialize compiled module with both pickle and dill")

    # Atomic replace
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        os.replace(tmp_path, filepath)
        logger.info(f"Compiled module saved to {filepath} ({used})")
    except Exception as e:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise RuntimeError(f"Failed to finalize serialization: {e}")
    return used


def load_compiled_module(filepath: str) -> Optional[Any]:
    """Load previously compiled DSPy module using recorded serializer."""
    if not os.path.exists(filepath):
        return None
    try:
        if os.path.getsize(filepath) < 64:
            logger.debug("Serialized file too small (<64B); treating as invalid cache")
            return None
    except OSError:
        return None
    serializer = "pickle"
    meta = _get_cache_metadata(filepath)
    if meta:
        serializer = meta.get("serializer", "pickle")

    def _pickle_loader():
        import pickle

        with open(filepath, "rb") as f:
            return pickle.load(f)

    def _dill_loader():
        import dill  # type: ignore

        with open(filepath, "rb") as f:
            return dill.load(f)  # type: ignore

    strategies: Dict[str, Callable[[], Any]] = {
        "pickle": _pickle_loader,
        "dill": _dill_loader,
    }
    order = [serializer] + [s for s in strategies.keys() if s != serializer]
    for strat in order:
        try:
            mod = strategies[strat]()
            logger.info(f"Compiled module loaded from {filepath} ({strat})")
            return mod
        except Exception as e:
            logger.warning(f"Failed to load with {strat}: {e}")
            continue
    logger.error("All deserialization strategies failed for %s", filepath)
    return None


def clear_cache(cache_path: str = "logs/compiled_supervisor.pkl"):
    """Clear compiled module cache.

    Args:
        cache_path: Path to cache file to clear
    """
    try:
        if os.path.exists(cache_path):
            os.remove(cache_path)
            logger.info(f"Cache file removed: {cache_path}")

        metadata_path = cache_path + ".meta"
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            logger.info(f"Cache metadata removed: {metadata_path}")
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")


def get_cache_info(
    cache_path: str = "logs/compiled_supervisor.pkl",
) -> Optional[Dict[str, Any]]:
    """Get information about cached module.

    Args:
        cache_path: Path to cache file

    Returns:
        Dictionary with cache information or None
    """
    if not os.path.exists(cache_path):
        return None

    metadata = _get_cache_metadata(cache_path)
    cache_mtime = os.path.getmtime(cache_path)
    cache_size = os.path.getsize(cache_path)

    info = {
        "cache_path": cache_path,
        "cache_size_bytes": cache_size,
        "cache_mtime": datetime.fromtimestamp(cache_mtime).isoformat(),
    }

    if metadata:
        info.update(metadata)

    return info
