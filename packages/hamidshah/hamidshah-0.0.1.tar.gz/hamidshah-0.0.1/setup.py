from setuptools import setup

with open("README.md", "r") as fh:
    description = fh.read()

setup(
    name="hamidshah",
    version="0.0.1",
    author="Hamidreza",
    author_email="hshahzamanian@gmail.com",
    packages=["hamidshah"],
    description="A sample hamidshah",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/gituser/hamidshah",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)