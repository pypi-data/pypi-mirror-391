from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='brnltk',
    version='3.1.2',
    description='A Part-of-Speech Tagger and Dialect Processing Toolkit for Bengali.',
    long_description=long_description,  # <-- Display README on PyPI
    long_description_content_type='text/markdown',
    author='Mahmudul Haque Shakir',
    author_email='mahmudulhaqueshakir@gmail.com',
    url='https://github.com/ShakirHaque/brposNLTK',  # <-- your repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'tensorflow>=2.10.0',
        'openpyxl>=3.0.0'
    ],
    extras_require={
        "dev": [
            "keras>=2.12.0",
            "scikit-learn>=1.2.0"
        ],
        "testing": [
            "pytest>=7.0.0"
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Bengali'
    ],
    python_requires='>=3.6',
)
