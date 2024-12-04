from setuptools import setup, find_packages

setup(
    name='your_project_name',
    use_scm_version=True,
    packages=find_packages(),
    install_requires=[
        'PySide6',
        'Appium-Python-Client',
        'openai',
        'pydantic',
    ],
    extra_requires={
        'dev': [
            'pyinstaller',
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
