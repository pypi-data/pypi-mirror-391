from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")


setup(
    name='gilgamesh_summarizer',
    version='0.2.7',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'unsloth',
        'transformers',
        'torch',
        'networkx',
        'tqdm',
        'pandas',
        'pyjedai',
    ],
    python_requires='>=3.10',
    author='Kostas Plas',
    author_email='kplas@di.uoa.gr',
    description='A package for summarizing RDF graphs for Question Answering pipelines',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
