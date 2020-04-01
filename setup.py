import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ase_grain",
    version="0.0.1",
    author="Harry Zhang",
    author_email="zhanghar@iu.edu",
    description="An async wrapper for ASE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Contextualist/ase-grain",
    packages=setuptools.find_packages(),
    install_requires=[
        "ase @ git+https://gitlab.com/ase/ase.git@f4a9a424#egg=ase-f4a9a424",
        "grain-scheduler >= 0.11.0"
    ],
    tests_require = [
        "pytest",
        "pytest-trio",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Framework :: Trio",
        "Framework :: AsyncIO",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
)
