from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for a detailed PyPI description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="rocketformulas",
    version="1.0.0",
    author="Amandeep Singh, Tuiba Ashraf",
    author_email="amandeepoct97@gmail.com,tuiba.ashraf107@gmail.com",
    description="A Python library providing basic formulas for rocket engine performance and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "matplotlib>=3.7.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    
    ],

)

