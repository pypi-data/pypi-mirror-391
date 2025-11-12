from setuptools import setup, find_packages

setup(
    name="pranavi-convert",
    version="0.1.0",
    author="Puneeth Kumar",
    author_email="your_email@example.com",
    description="A universal data converter (binary, hex, octal, ascii)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourgithubusername/pranavi-convert",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
