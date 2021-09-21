import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypely",
    version="0.0.1",
    description="Make your data processing easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stoney95/pype",
    author="Stoney95",
    author_email="simon@steinheber.info",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={'': 'src'},
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        'dev': []
    },
)