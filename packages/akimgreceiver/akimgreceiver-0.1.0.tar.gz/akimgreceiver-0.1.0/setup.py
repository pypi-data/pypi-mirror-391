from setuptools import setup, find_packages

setup(
    name="akimgreceiver",
    version="0.1.0",
    description="Simple image receiver that reads latest frame.png and deletes it.",
    author="Akshay Ajit Bhawar",
    packages=find_packages(),
    python_requires=">=3.7",
)
