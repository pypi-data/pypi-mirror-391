import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

__version__ = "5.19.2"

setuptools.setup(
    name="xyz_py",
    version=__version__,
    author="Jon Kragskow",
    author_email="jonkragskow@gmail.com",
    description="A package for manipulating xyz files and chemical structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/jonkragskow/xyz_py",
    project_urls={
        "Bug Tracker": "https://gitlab.com/jonkragskow/xyz_py/-/issues",
        "Documentation": "https://jonkragskow.gitlab.io/xyz_py"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license='GPL-3.0-or-later',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "ase",
    ],
    entry_points={
        'console_scripts': [
            'xyz_py = xyz_py.cli:main'
        ]
    }
)
