from setuptools import setup, find_packages

setup(
    name="versalaw2",
    version="3.0.1",
    author="VersaLaw Team",
    description="Legal Analysis System",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
)
