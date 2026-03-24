from setuptools import setup, find_packages

setup(
    name="autoops",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "autoops=autoops.cli:main"
        ]
    },
)