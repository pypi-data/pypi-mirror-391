# File: setup.py

from setuptools import setup, find_packages
import os

# Function to read the README file
def read(fname):
    # --- THIS IS THE FIX ---
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()
    # ---------------------

setup(
    name="my-text-emojifier",
    version="0.1.0",
    author="Saurabh Pandey",
    description="A simple library to replace or append emojis to text using NLTK",
    
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    
    packages=find_packages(),
    
    keywords=['emoji', 'text', 'nlp', 'replacer', 'nltk'],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
    ],
    python_requires='>=3.6',
    
    install_requires=[
        "nltk>=3.6"
    ],
)