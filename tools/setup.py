from setuptools import setup, find_packages

setup(
    name="tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "Pillow",
        "pygame",
        "pyinstaller",
    ],
)
