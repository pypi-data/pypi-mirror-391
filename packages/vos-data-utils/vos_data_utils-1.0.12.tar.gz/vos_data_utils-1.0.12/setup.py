import setuptools
from vdutils import (
    author,
    version,
    description,
    license
)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vos-data-utils",
    version=version,
    author=author,
    author_email="dev@valueofspace.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={"vdutils": [
        "data/bjd/*/*.txt", 
        "data/date/*.txt"
    ]},
    classifiers=[
        f"License :: OSI Approved :: {license}",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires='>=3.8',
    install_requires=[
        "symspellpy",
        "pandas",
        "requests",
        "python-dotenv"
    ],
    entry_points={
        'console_scripts': [
            'shortcut1 = package.module:func',
        ],
        'gui_scripts': [
            'shortcut2 = package.module:func',
        ]
    }
)
