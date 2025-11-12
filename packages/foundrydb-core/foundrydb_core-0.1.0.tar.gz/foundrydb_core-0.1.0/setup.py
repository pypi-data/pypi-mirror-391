from setuptools import setup, find_packages

setup(
    name="foundrydb-core",
    version="0.1.0",
    author="Alinani Simukanga",
    description="A tiny educational SQL engine written in pure Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/a1inani/foundrydb",
    license="MIT",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    python_requires=">=3.11",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "ruff",
            "mypy",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database :: Database Engines/Servers",
        "Intended Audience :: Education",
    ],
    entry_points={
        "console_scripts": [
            "foundrydb-cli=foundrydb.cli:main",
        ],
    },
)
