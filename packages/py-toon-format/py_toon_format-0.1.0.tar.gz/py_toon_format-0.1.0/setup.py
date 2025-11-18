"""Setup script for py-toon-format"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-toon-format",
    version="0.1.0",
    author="Ertugrul Kara",
    author_email="ertugrulkra@gmail.com",  # TODO: Gerçek email adresinizi ekleyin
    description="Python implementation of Token-Oriented Object Notation (TOON)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErtugrulKra/py-toon-format",  # TODO: GitHub repo URL'inizi ekleyin
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "llm": [
            "tiktoken>=0.5.0",  # For accurate token counting
        ],
    },
    entry_points={
        "console_scripts": [
            "py-toon=py_toon_format.cli:main",
        ],
    },
)

