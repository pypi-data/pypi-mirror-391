from setuptools import setup, find_packages

setup(
    name="task-manager-saqib",  
    version="1.0.0",
    author="Saqib Raheem(ws)",
    author_email="your_email@example.com",
    description="A simple Python task manager library for adding, removing, and updating tasks.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/task-manager-saqib/", 
    packages=find_packages(),
    python_requires=">=3.6",
)
