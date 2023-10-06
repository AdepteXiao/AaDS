
# pylint: disable=C0114

from distutils.core import setup
from Cython.Build import cythonize


setup(
    name='my_array',
    ext_modules=cythonize("my_array.pyx"),
)