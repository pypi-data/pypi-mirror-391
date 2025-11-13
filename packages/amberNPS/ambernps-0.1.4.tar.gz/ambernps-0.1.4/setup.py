from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name = 'amberNPS',
    packages = ['amberNPS'],
    include_package_data=True,
    package_data= {'amberNPS': ['*.pkl', '*.png']},
    version = '0.1.4',
    license='MIT',
    description = 'A python api to make lethal blood concentrations using amberNPS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Daniel Pasin',
    author_email = 'daniel.pasin@hyperiondata.org',
    url = 'https://github.com/dpasin/amberNPS-api',
    keywords = ['amberNPS', 'chemistry', 'toxicology'],
    install_requires=['numpy', 'pandas', 'rdkit', 'mordredcommunity', 'scikit-learn==1.6.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Programming Language :: Python',
    ],
)