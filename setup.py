import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deeptigargb-deepti", # Replace with your own username
    version="0.0.1",
    author="Deepti Garg",
    author_email="garg.deepti996@gmail.com",
    description="Trying Small personal package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deeptigargb/deeptigargb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)