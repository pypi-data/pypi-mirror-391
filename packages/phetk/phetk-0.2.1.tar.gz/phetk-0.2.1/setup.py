from setuptools import setup, find_packages

# Read the content of the README.md file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='phetk',
    # version='0.1.47',
    version='0.2.1',
    python_requires='>=3.7',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        '': ['*.*'],
        'phetk': ['phecode/*'],
    },
    url='https://github.com/nhgritctran/PheTK',
    license='GPL-3.0',
    author='Tam Tran',
    author_email='PheTK@mail.nih.gov',
    description='The Phenotype Toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "adjusttext",
        "connectorx",
        "google-cloud-bigquery",
        "google-cloud-storage",
        "hail",
        "lifelines",
        "lxml",
        "matplotlib",
        "numpy",
        "pandas",
        "polars",
        "psutil",
        "pyarrow>=10.0.1",
        "statsmodels",
        "tqdm"
    ],
    entry_points={
        'console_scripts': [
            'phetk=phetk.__main__:main',
        ],
    }
)
