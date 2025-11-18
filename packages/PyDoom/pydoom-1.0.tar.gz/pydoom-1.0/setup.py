from setuptools import setup, find_packages

setup(
    name="PyDoom",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.0.0"
    ],
    description="Create easy doom-like game on python",
    python_requires='>=3.8'
)
