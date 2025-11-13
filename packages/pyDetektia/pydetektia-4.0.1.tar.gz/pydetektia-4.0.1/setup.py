from setuptools import setup

setup(
    name='pyDetektia',
    version='4.0.1',
    url='https://github.com/detektia/pyDetektia',
    author='Detektia',
    author_email='info@detektia.com',
    packages=['pyDetektia'],
    install_requires=['requests'],
    license='ToBeChosen',
    description="A package for easily interaction with Detektia's API endpoints.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)