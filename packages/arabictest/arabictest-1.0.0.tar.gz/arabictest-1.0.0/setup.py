"""
Arabic Unit Root Testing Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/arabictest
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="arabictest",
    version="1.0.0",
    author="Dr. Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="Professional unit root testing package with Arabic language support for econometric research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/arabictest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "statsmodels>=0.13.0",
        "arch>=5.0.0",
        "tabulate>=0.8.9",
        "prettytable>=3.0.0",
        "arabic-reshaper>=2.1.0",
        "python-bidi>=0.4.2",
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    keywords=[
        "econometrics",
        "unit root test",
        "time series",
        "ADF test",
        "KPSS test",
        "Phillips-Perron",
        "stationarity",
        "Arabic",
        "statistics",
    ],
)
