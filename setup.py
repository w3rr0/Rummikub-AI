from setuptools import setup, Extension
import pybind11

cpp_args = ['-std=c++17', '-O3']
linker_args = []


ext_modules = [
    Extension(
        'rummikub_solver',
        [
            'cpp/validation.cpp',
            'cpp/solver.cpp',
            'cpp/bindings.cpp'
        ],
        include_dirs=[
            'cpp',
            pybind11.get_include()
        ],
        language='c++',
        extra_compile_args=cpp_args,
    ),
]

setup(
    name='rummikub_solver',
    version='1.1',
    description='A C++ extension for solving Rummikub moves',
    ext_modules=ext_modules,
)