from setuptools import setup, find_packages

setup(
    name="elonify",
    version="0.0.1",
    description="The one-liner web toolkit that auto-thinks like Elon.",
    author="Legen",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4"],
)
