import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

__version__ = "0.2.2"

setuptools.setup(
    name="pypely",
    version=__version__,
    description="Make data processing easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stoney95/pypely",
    author="Stoney95",
    author_email="simon@steinheber.info",
    license="GPLv3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={'': 'src'},
    package_data={'': ["*.html"]},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "beautifulsoup4",        
        "IPython"
        "isort==5.11.4"
    ],
    extras_require={
        'dev': []
    },
)