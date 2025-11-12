# ============================================
# setup.py
# ============================================
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dsf-aml-sdk",
    version="2.1.0",  # Nueva versión para PyPI
    author="Jaime Alexander Jimenez",
    author_email="contacto@dsfuptech.cloud",
    description="DSF AML SDK — Automated ML Robustness & Failure Correction Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dsfuptech.cloud",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",  # 🔹 Cambiado (antes decía MIT)
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="dsf aml ml machine-learning robustness auto-healing sdk",
    license="Proprietary",  # 🔹 Añadido explícitamente
)
