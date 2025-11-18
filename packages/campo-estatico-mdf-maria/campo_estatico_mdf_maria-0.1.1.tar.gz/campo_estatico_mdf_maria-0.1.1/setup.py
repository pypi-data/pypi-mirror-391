"""
Setup script para el paquete campo_estatico_mdf.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="campo_estatico_mdf_maria",
    version="0.1.1",
    author="Maria Moreno , Sebastian Sanchez",
    author_email="maamorenor@udistrital.edu.co",
    description="Solución de la ecuación de Laplace en 2D usando el Método de Diferencias Finitas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://almarm-r.github.io/campo_estatico_mdf/introduccion.html",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
)
