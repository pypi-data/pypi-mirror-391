from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='ligrad',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        "numpy>=2.2",
        "scipy>=1.15",
        "astropy>=7.0",
        "pylightcurve>=4.0"
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)