from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name ="MLOPS-PROJECT-2",
    version=1,
    author = "raj",
    packages=find_packages(),
    install_requires = requirements,
)