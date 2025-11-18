from setuptools import find_packages  # type: ignore
from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dspy-agent-framework",
    version="0.1.0",
    author="Zochory",
    author_email="zochory@example.com",
    description="DSPy-enhanced multi-agent workflow system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zochory/dspy-agent-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=[
        "dspy>=3.0.3",
        "openai>=2.7.1",
        "agent-framework>=0.1.0",
        "tavily-python>=0.7.12",
        "pydantic>=2.12.3",
        "pyyaml>=6.0.3",
        "python-dotenv>=1.2.1",
        "rich>=14.2.0",
        "typer>=0.20.0",
        "textual>=6.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dspy-fleet=cli.fleet:main",
        ],
    },
)
