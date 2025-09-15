import sys

from setuptools import setup, Extension
import pybind11

extra_compile_args = []
linker_args = []

if sys.platform == "win32":
    extra_compile_args = ["/std:c++17", "/02"]
else:
    extra_compile_args = ["-std=c++17", "-O3"]

ext_modules = [
    Extension(
        'rummikub_solver',
        [
            'cpp/validation.cpp',
            'cpp/solver.cpp',
            'cpp/bindings.cpp',
            'cpp/GameEngine.cpp'
        ],
        include_dirs=[
            'cpp',
            pybind11.get_include()
        ],
        language='c++',
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name='rummikub_solver',
    version='1.1',
    description='A C++ extension for solving Rummikub moves',
    ext_modules=ext_modules,
)