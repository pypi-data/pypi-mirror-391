from setuptools import setup, find_packages

# Read the README.md file from the parent directory
with open("./README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hdc_installer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "hdc_installer=hdc_installer.cli:main",
        ],
    },
    author="youngfreefjs",
    author_email="youngfreefjs@gmail.com",
    description="A lightweight installer for HarmonyOS HDC tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youngfreeFJS/harmony_hdc_bin_collection",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)