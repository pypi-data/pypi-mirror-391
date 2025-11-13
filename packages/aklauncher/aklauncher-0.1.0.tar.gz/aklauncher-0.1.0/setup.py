# setup.py
from setuptools import setup, find_packages

setup(
    name="aklauncher",
    version="0.1.0",
    description="Simple Windows-only launcher that opens multiple Python scripts in separate CMD windows.",
    author="Akshay Ajit Bhawar",
    packages=find_packages(),
    python_requires=">=3.6",
)
