import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

requirements = []
with open("requirements.txt", "r") as f:
    for line in f:
        if line[0] == '#':
            continue
        line = line.strip()
        if line:
            requirements.append(line)

setuptools.setup(
    name="datacommon",
    version="0.0.1",
    author="JanusLin",
    author_email="j4nusl1n@gmail.com",
    description="Common packages for easily setting up utilities",
    long_description=long_description,
    url="https://github.com/j4nusl1n/common-util.git",
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    exclude_package_data={
        "": ["test_*.py"]
    },
    install_requires=requirements
)