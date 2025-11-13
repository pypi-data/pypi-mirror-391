import setuptools


# Requirements
def get_requirements():
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
        return requirements


setuptools.setup(
    install_requires=get_requirements(),
)
