"""
Setup script for RBFMVAR package.
"""

from setuptools import setup, find_packages
import os

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='rbfmvar',
    version='1.0.2',
    author='Dr. Merwan Roudane',
    author_email='merwanroudane920@gmail.com',
    description='Residual-Based Fully Modified Vector Autoregression for mixtures of I(0), I(1), and I(2) processes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/merwanroudane/RBFMVAR',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='econometrics VAR cointegration I(2) time-series nonstationary',
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
            'sphinx>=4.0',
            'sphinx-rtd-theme>=0.5',
        ],
        'plotting': [
            'matplotlib>=3.3',
            'seaborn>=0.11',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Bug Reports': 'https://github.com/merwanroudane/RBFMVAR/issues',
        'Source': 'https://github.com/merwanroudane/RBFMVAR',
        'Documentation': 'https://github.com/merwanroudane/RBFMVAR#readme',
    },
)
