from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wouaka",
    version="1.0.0",
    author="Wouaka SAS",
    author_email="support@wouaka.com",
    description="SDK Python officiel pour l'API Wouaka - Scoring crédit et KYC pour l'Afrique de l'Ouest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wouaka/wouaka-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
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
        "requests>=2.28.0",
        "python-dateutil>=2.8.2",
        "pydantic>=2.0.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="wouaka credit-scoring kyc verification africa uemoa fintech microfinance",
    project_urls={
        "Bug Reports": "https://github.com/wouaka/wouaka-python-sdk/issues",
        "Documentation": "https://docs.wouaka.com",
        "Source": "https://github.com/wouaka/wouaka-python-sdk",
    },
)
