# versalaw2/setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="versalaw2",
    version="2.0.4",  # Naikkan version untuk update description
    author="Maya Legal Systems",
    author_email="your-email@example.com",
    description="Advanced Indonesian Legal AI with Ghost Contract Analysis & 100+ Expert Study Cases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        'versalaw2': [
            'legal_knowledge/advanced_cases/*.md',
            'legal_knowledge/law_library/*.md',
            'legal_knowledge/supreme_analysis/*.md',
        ],
    },
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[],
)
