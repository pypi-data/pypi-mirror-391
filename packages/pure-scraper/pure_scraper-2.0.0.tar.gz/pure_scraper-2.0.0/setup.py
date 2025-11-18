# setup.py
from setuptools import setup, find_packages


with open("README.md","r", encoding="utf-8") as f:
    description=f.read()

setup(
    name="pure-scraper",
    version="2.0.0",
    packages=find_packages(),
    description="A lightweight pure Python HTML scraper and parser.",
    author="Rohit",
    author_email="rohitkumar@devexhub.in",
    license="MIT",
    python_requires=">=3.7",
    entry_points={
        "console_scripts":{
            "pure-scraper = pure_scraper.cli:main",
        },
    },

    long_description=description,
    long_description_content_type="text/markdown",
)
