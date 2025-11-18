from setuptools import setup, find_packages

setup(
    name="SMARK_ON",
    version="0.1.0",
    packages=find_packages(),
    description="اجر",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SMARK",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Android",
    ],
)