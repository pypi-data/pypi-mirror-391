from pathlib import Path
from setuptools import setup, find_packages

#README.md file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="automl_optuna_demo",  
    version="0.1.1",
    author="Vaishnav Naik",     
    description="A simple AutoML demo using Optuna and Scikit-learn",  
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "optuna",
        "scikit-learn"
    ],
    python_requires=">=3.8",   
)