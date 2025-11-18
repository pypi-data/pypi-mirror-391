from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neatify",
    version="1.0.1",
    author="Anmol Jhamb",
    author_email="talktoanmol@outlook.com",
    description="A CLI tool to organize files by their extensions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anmoljhamb/neatify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "neatify=neatify.cli:main",
        ],
    },
)
