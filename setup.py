from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thumbup',
    version='1.5.1',
    description='A convenient video thumbnails generator.',
    license='MIT',
    long_description=long_description,
    url='https://github.com/bl4ck5un/thumbup.py',
    author='Fan Zhang',
    author_email='bl4ck5unxx@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='video thumbnail snapshot',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['Pillow', 'av', 'numpy'],
    entry_points={
        'console_scripts': [
            'thumbup=thumbup.cmd_line:main',
        ],
    },
)
