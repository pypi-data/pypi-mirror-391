from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name = 'amberNPS',
    packages = ['amberNPS'],
    version = '0.1.2',
    license='MIT',
    description = 'A python api to make lethal blood concentrations using amberNPS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Daniel Pasin',
    author_email = 'daniel.j.pasin@outlook.com',
    url = 'https://github.com/dpasin/amberNPS-api',
    keywords = ['amberNPS', 'chemistry', 'toxicology'],
    install_requires=['numpy', 'pandas', 'rdkit', 'mordredcommunity', 'scikit-learn==1.6.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)