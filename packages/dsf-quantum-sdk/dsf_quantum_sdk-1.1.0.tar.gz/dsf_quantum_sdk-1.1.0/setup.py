# setup.py
"""Setup configuration for PyPI"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dsf-quantum-sdk",
    version="1.1.0",
    author="Jaime Alexander Jimenez",
    author_email="contacto@dsfuptech.cloud",
    description="Lightweight SDK for DSF Quantum Adaptive Scoring with IBM Quantum support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaimeajl/dsf-quantum-sdk",
    packages=find_packages(exclude=["examples", "tests", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "pytest-asyncio>=0.18",
        ]
    },
    keywords=[
        "quantum",
        "quantum computing",
        "ibm quantum",
        "qiskit",
        "adaptive scoring",
        "hierarchical evaluation",
        "quantum amplitude estimation",
        "qae",
        "dsf",
        "decision support",
        "machine learning",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/jaimeajl/dsf-quantum-sdk/issues",
        "Documentation": "https://docs.jaimeajl.com/dsf-quantum-sdk",
        "Source Code": "https://github.com/jaimeajl/dsf-quantum-sdk",
        "Examples": "https://github.com/jaimeajl/dsf-quantum-sdk/tree/main/examples",
    },
)