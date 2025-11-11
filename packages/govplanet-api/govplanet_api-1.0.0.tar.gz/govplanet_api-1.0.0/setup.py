from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="govplanet-api",
    version="1.0.0",
    author="Jonathan Gan",
    author_email="jonny2298@live.com",
    description="A complete reverse-engineered API client for GovPlanet with extensive product search capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/govplanet-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="govplanet api client search products auction",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/govplanet-api/issues",
        "Source": "https://github.com/yourusername/govplanet-api",
        "Documentation": "https://github.com/yourusername/govplanet-api#readme",
    },
)

