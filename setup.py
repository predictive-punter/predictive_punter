from codecs import open
from os import path
from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='predictive_punter',
    version='1.0.0a5',
    description='Applying predictive analytics to horse racing via Python',
    long_description=long_description,
    keywords='predictive analytics horse racing',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    url='https://github.com/justjasongreen/predictive_punter',
    author='Jason Green',
    author_email='justjasongreen@gmail.com',
    license='MIT',

    packages=find_packages(exclude=['tests']),
    setup_requires=[],
    install_requires=[
        'cache_requests',
        'lxml',
        'numpy',
        'punters_client',
        'pymongo',
        'racing_data',
        'redis',
        'requests',
        'scikit-learn',
        'scipy'
    ],
    extras_require={
        'dev':  [
            'bumpversion',
            'check-manifest'
        ],
        'test': [
            'tox'
        ]
    },
    package_data={
        'predictive_punter':   []
    },
    data_files=[],
    entry_points={
        'console_scripts':  [
            'scrape=predictive_punter.scrape:main',
            'seed=predictive_punter.seed:main',
            'simulate=predictive_punter.simulate:main'
        ]
    }
    )
