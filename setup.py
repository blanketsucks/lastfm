from setuptools import setup

setup(
    name='lastfm',
    version='0.1.0',
    description='An asynchronous wrapper for the last.fm API.',
    packages=['lastfm'],
    python_requires='>=3.8',
    install_requires=['aiohttp']
)