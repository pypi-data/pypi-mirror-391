from setuptools import Extension, setup
import platform

if platform.system() == 'Windows':
    extra_flags = ['/openmp']
    extra_link = []
elif platform.system() != 'Darwin':
    extra_flags = ['-fopenmp']
    extra_link = ['-lgomp']
else:
    extra_flags = []
    extra_link = []

setup(
    ext_modules=[
        Extension(
            'brifc',
            ['pybrif.c', 'brif.c'],
            extra_compile_args=extra_flags,
            extra_link_args=extra_link,
        )
    ],
)
