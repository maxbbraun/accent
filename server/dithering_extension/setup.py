from setuptools import Extension
from setuptools import setup
from numpy import get_include

extension = Extension(
    name='dithering',
    sources=['dithering.c'],
    include_dirs=[get_include()])

setup(ext_modules=[extension])
