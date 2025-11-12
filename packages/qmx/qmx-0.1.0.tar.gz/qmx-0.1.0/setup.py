# setup.py
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys

ext_modules = [
    Extension(
        'c_matmul',
        sources=[
            'csrc/matmul.c',
            'csrc/bindings.c',
        ],
        include_dirs=['csrc'],
        extra_compile_args=['-O3', '-std=c11'] if sys.platform != 'win32' else ['/O2'],
    ),
]

setup(
    name='qmx',
    version='0.1.0',
    author='TBD',
    description='Pure C accelerated matrix operations for LLMs',
    package_data={'mx': ['*.py']},
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/micwill755/mtrx',
    package_dir={'': 'src'},
    packages=['mx'],
    py_modules=['c_matmul'],
    ext_modules=ext_modules,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'Programming Language :: C',
    ],
)
