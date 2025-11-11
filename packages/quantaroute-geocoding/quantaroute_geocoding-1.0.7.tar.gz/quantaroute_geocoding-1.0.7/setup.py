from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantaroute-geocoding",
    version="1.0.7",
    author="QuantaRoute",
    author_email="hello@quantaroute.com",
    description="Revolutionary Python SDK for QuantaRoute Geocoding API with Location Lookup and offline DigiPin processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quantaroute/quantaroute-geocoding-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0",
        "digipin>=1.0.0",  # The official DigiPin library
        "tqdm>=4.60.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "quantaroute-geocode=quantaroute_geocoding.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "quantaroute_geocoding": ["*.json", "*.yaml"],
    },
)
