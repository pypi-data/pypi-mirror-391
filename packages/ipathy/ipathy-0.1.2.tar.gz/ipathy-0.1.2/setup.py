from setuptools import setup, find_packages

setup(
    name="ipathy",
    version="0.1.2",
    author="PyBeast",
    author_email="pybeast@example.com",
    description="The path fixer your OS forgot — cross-platform path normalizer for Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    license="MIT",
)
