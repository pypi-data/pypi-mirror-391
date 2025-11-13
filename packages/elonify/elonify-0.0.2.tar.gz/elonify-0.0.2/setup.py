from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="elonify",
    version="0.0.2",
    description="The one-liner web toolkit that auto-thinks like Elon.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Legen",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4"],
    url="https://github.com/abrlake/elonify",  # optional but nice to have
)
