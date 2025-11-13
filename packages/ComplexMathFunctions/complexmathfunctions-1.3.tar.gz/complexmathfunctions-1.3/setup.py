from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding ='utf-8') as f:
    long_description = f.read()

setup(
    name = "ComplexMathFunctions",
    version = "1.3",
    author = "Enes5234r",
    description = "Complex math",
    long_description=  long_description,
    long_description_content_type= "text/markdown",
    author_email = "bayintinkercadhesabi@gmail.com",
    packages = find_packages(),
    install_requires = []
)