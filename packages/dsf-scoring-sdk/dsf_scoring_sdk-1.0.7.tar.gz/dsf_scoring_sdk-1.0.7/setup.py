# ============================================
# setup.py — DSF Scoring SDK
# ============================================
from setuptools import setup, find_packages
import os

# Leer README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dsf-scoring-sdk",  # Nombre visible en PyPI
    version="1.0.7",
    author="Jaime Alexander Jimenez",
    author_email="contacto@dsfuptech.cloud",
    description="Adaptive Credit Scoring SDK for DSF Robust ML System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaimeajl/dsf-scoring-sdk",
    project_urls={
        "Documentation": "https://dsfuptech.cloud/docs",
        "Source": "https://github.com/jaimeajl/dsf-scoring-sdk",
        "API Endpoint": "https://dsf-scoring-2s5xthc9q-api-dsfuptech.vercel.app/api/",
    },
    packages=find_packages(include=["dsf_scoring_sdk", "dsf_scoring_sdk.*"]),
    include_package_data=True,
    license="Proprietary License © 2025 Jaime Alexander Jimenez (Uptech)",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="dsf scoring sdk machine-learning credit risk api adaptive robustness",
)
