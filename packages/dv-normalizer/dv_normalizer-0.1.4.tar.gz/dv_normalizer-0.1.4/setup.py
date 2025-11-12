from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="dv_normalizer",
    version="0.1.4",
    description="A Python library for normalizing Dhivehi text and converting numbers to Dhivehi text format, supporting written, spoken and year forms",
    author="Alakxender",
    author_email="alakxender@gmail.com",
    packages=find_packages(),
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "dv_normalize": ["*.yaml", "*.json", "configs/*"],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)