from setuptools import setup, find_packages

setup(
    name="ml_agreement",
    version="1.0.0",
    packages=find_packages(),
    description="A metric to calculate inter-annotator agreement for scenarios where several labels can be simultaneously assigned to an item",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tim Menzner",
    author_email="tim.menzner@hs-coburg.de",
    url="https://github.com/Timperator2/Multi-Label-Agreement",
    python_requires=">=3.6",
)
