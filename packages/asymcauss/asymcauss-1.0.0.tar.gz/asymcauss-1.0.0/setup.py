from setuptools import setup, find_packages

setup(
    name="asymcauss",
    version="1.0.0",
    author="Dr. Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="Asymmetric Causality Tests compatible with GAUSS implementation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/asymcauss",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.6.0",
        "statsmodels>=0.13.0",
        "matplotlib>=3.4.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.7",
)
