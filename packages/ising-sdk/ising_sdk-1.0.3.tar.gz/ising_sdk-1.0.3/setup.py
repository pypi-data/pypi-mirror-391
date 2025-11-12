from setuptools import setup, find_packages

setup(
    name="ising_sdk",
    version="1.0.3",
    packages=find_packages(),
    install_requires=[
        'requests>=2.22.0',
    ],
    python_requires='>=3.6',
    author="ising",
    author_email="haojunjie@isingtech.com",
    description="Python SDK for Ising Cloud Service",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)