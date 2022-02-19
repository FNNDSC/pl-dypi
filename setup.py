from setuptools import setup

setup(
    name             = 'dypi',
    version          = '1.1.2',
    description      = 'A ChRIS DS plugin that grows compute trees during execution',
    author           = 'FNNDSC',
    author_email     = 'dev@babyMRI.org',
    url              = 'https://github.com/FNNDSC/pl-dypi',
    py_modules       = ['app'],
    install_requires = ['chris_plugin'],
    license          = 'MIT',
    python_requires  = '>=3.8.2',
    packages         = ['control', 'logic', 'state'],
    entry_points     = {
        'console_scripts': [
            'dypi = app:main'
            ]
        },
    classifiers      = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
