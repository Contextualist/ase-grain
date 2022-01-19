import setuptools

exec(open("ase_grain/_version.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ase-grain",
    version=__version__,
    author="Harry Zhang",
    author_email="zhanghar@iu.edu",
    description="An async wrapper for ASE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Contextualist/ase-grain",
    packages=setuptools.find_packages(),
    install_requires=[
        "ase >= 3.21.0, < 3.22.0",
        "grain-scheduler >= 0.12.1",
        "trio",
    ],
    tests_require=[
        "pytest",
        "pytest-trio",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Trio",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
)
