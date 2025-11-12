"""
VocaFuse Python SDK Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="vocafuse",
    version="0.1.0",
    description="A Python module for communicating with the VocaFuse API and building voice-enabled applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VocaFuse",
    author_email="support@vocafuse.com",
    url="https://github.com/VocaFuse/vocafuse-python",
    project_urls={
        "Bug Tracker": "https://github.com/VocaFuse/vocafuse-python/issues",
        "Documentation": "https://github.com/VocaFuse/vocafuse-python#readme",
        "Source Code": "https://github.com/VocaFuse/vocafuse-python",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    keywords="vocafuse voice api sdk transcription audio speech",
    include_package_data=True,
)
