"""
Setup script for TIA Signal Automator SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mudrex-signal-automator",
    version="1.0.0",
    author="Trade Ideas Automation Service",
    description="Receive live trading signals and execute automatically on Mudrex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "signal-sdk=tia_sdk.cli:main",
        ],
    },
    include_package_data=True,
)
