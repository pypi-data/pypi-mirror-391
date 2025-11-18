from setuptools import setup, find_packages

setup(
    name="clockitpy",
    version="0.1.0",
    author="Unknon Man",
    author_email="unknonmanbro@gamil.com",
    description="A lightweight Python library to measure function execution time.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
)
