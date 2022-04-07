import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="planar-magnetics",
    version="0.1.0",
    author="Donny Zimmanck",
    author_email="dzimmanck@gmail.com",
    description="Create planar magnetic structures programmatically and export to CAD tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dzimmanck/python-planar-magnetics",
    project_urls={
        "Bug Tracker": "https://github.com/dzimmanck/python-planar-magnetics/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=["ezdxf>=0.17.2"],
    extras_require={"dev": ["pytest",],},
    python_requires=">=3.7",
)
