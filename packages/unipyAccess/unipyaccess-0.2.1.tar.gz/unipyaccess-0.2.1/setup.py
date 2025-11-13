from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='unipyAccess',
    version='0.2.1',  # Placeholder for the version
    packages=find_packages(),
    install_requires=[
        'requests==2.32.3'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
