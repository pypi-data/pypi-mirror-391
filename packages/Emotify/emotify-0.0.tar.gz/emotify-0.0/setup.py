from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='Emotify',
    version='0.0',
    packages=find_packages(),
    install_requires=[
        're',
    ],  # Add a comma here
    author='Saurabh Pandey',

    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
)
