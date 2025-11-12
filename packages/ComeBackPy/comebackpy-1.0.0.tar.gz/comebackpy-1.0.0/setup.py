from setuptools import setup, find_packages

setup(
    name="ComeBackPy",
    version="1.0.0",
    author="Hemil Patel",
    description="A Python SDK for interacting with the ComeBackPy API",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
)
    