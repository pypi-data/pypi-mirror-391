from setuptools import setup, find_packages

setup(
    name='simpledqn',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'torch>=1.9.0',
        'gymnasium',
        'matplotlib'
    ],
    description='A simple DQN implementation for reinforcement learning beginners',
    author='Shiv Shah',
    author_email='shivshah1917@gmail.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
