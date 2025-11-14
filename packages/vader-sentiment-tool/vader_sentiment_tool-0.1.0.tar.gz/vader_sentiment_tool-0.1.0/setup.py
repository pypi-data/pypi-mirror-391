from setuptools import setup, find_packages

setup(
    name='vader-sentiment-tool',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple sentiment analyzer using VADER',
    packages=find_packages(),
    install_requires=['vaderSentiment'],
    python_requires='>=3.7',
)
