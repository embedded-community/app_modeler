from os import path

from setuptools import setup, find_packages

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='app_modeler',
    use_scm_version=True,
    author='Jussi Vatjus-Anttila',
    author_email='jussiva@gmail.com',
    setup_requires=['setuptools_scm'],
    description='application model generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/embedded-community/app_modeler',
    packages=find_packages(),
    install_requires=[
        'PySide6',
        'Appium-Python-Client',
        'openai',
        'pydantic',
    ],
    extras_require={
        'dev': [
            'pyinstaller',
            'ruff'
        ]
    },
    entry_points={
        'console_scripts': [
            'app_modeler=app_modeler:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
