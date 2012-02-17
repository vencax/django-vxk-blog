import os
from setuptools import setup, find_packages

install_requires = []
try:
    import json
except ImportError, e:
    install_requires.append('simplejson')

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README')

description = 'A small Django application that implements blogs functionality.'

if os.path.exists(README_PATH):
    long_description = open(README_PATH).read()
else:
    long_description = description


setup(
    name='django-vxk-blog',
    version='0.9.5',
    install_requires=install_requires,
    description=description,
    long_description=long_description,
    author='vencax',
    author_email='vencax@centrum.cz',
    url='https://github.com/vencax/django-vxk-blog',
    packages=['vxkblog'],
)
