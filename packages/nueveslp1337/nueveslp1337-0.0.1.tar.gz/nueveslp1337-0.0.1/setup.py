import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nueveslp1337",
    version="0.0.1",
    author="nueve",
    author_email="zakura.int@gmail.com",
    description="module for beautiful color in discord tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=['nueveslp1337'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)