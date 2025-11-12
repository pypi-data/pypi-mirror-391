from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
# Gets the long description from Readme file
long_description = (this_directory / "README.md").read_text()

setup(
    name='asciipal',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[],  # No external libraries needed!
    author='Neel Jaiswal',
    author_email='neelpjaiswal@gmail.com',
    description='A fun command-line tool that prints random ASCII art.',

    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',


    # This is the new section that makes the command-line tool work
    entry_points={
        'console_scripts': [
            'asciipal=asciipal.main:run',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Games/Entertainment",
    ]
)
