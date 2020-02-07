import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plantower",
    version="0.0.11",
    author="Philip Basford",
    author_email="P.J.Basford@soton.ac.uk",
    description="An interface for plantower particulate matter sensors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FEEprojects/plantower",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
     python_requires='>=3.3, <4',
     install_requires=['pyserial']
)
