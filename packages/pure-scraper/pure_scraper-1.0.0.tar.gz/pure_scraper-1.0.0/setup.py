# setup.py
from setuptools import setup, find_packages

setup(
    name="pure-scraper",
    version="1.0.0",
    packages=find_packages(),
    description="A lightweight pure Python HTML scraper and parser.",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    python_requires=">=3.7",
    entry_points={
        "console_scripts":{
            "pure-scraper = pure_scraper.cli:main"
        }
    }
)
