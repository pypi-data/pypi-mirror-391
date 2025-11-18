from setuptools import setup, find_packages

setup(
    name="Hello_Function",  
    version="1.0.0",
    author="Saqib Raheem(ws)",
    author_email="wsssaqib99@gmail.com",
    description="A simple Python task manager library for adding, removing, and updating tasks.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/Hello_function/", 
    packages=find_packages(),
    python_requires=">=3.6",
)
