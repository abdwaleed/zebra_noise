import platform
from setuptools import setup, Extension
import numpy as np

if platform.system() == "Windows":
    # MSVC (Windows C compiler) flags
    c_flags = ['/openmp', '/O2', '/fp:fast']
    l_flags = []
elif platform.system() == "Darwin":
    # macOS Apple Clang doesn't support OpenMP natively out of the box, 
    # so we fallback to standard maximum optimization
    c_flags = ['-O3', '-ffast-math']
    l_flags = []
else:
    # Linux (GCC) flags
    c_flags = ['-fopenmp', '-O3', '-ffast-math']
    l_flags = ['-fopenmp']

# 2. Define the C extension
perlin_module = Extension(
    name='zebranoise._perlin',
    sources=['zebranoise/_perlin.c'],
    include_dirs=[np.get_include()],         # Required so C knows what a NumPy array is
    extra_compile_args=c_flags,
    extra_link_args=l_flags
)

# 3. Setup the package
setup(
    name='zebranoise',
    version='0.1.2',
    description='Perlin noise video generator',
    packages=['zebranoise'],
    ext_modules=[perlin_module],
    install_requires=[
        'numpy',
        'scipy',
        'imageio',
        'tqdm'
    ],
)