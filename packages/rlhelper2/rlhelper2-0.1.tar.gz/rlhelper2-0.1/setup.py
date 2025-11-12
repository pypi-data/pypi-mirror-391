from setuptools import setup, find_packages

setup(
    name='rlhelper2', 
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    description='A small RL helper function for reward normalization',
    long_description='This package helps normalize rewards between 0 and 1 for reinforcement learning experiments.',
    long_description_content_type='text/markdown',
    author='Devaansh Shukla',
)
