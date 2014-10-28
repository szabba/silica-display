from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
        name='silica',
        url='bitbucket.org/szabba/silica_display',
        version='0.3',

        author='Karol Marcjan',
        author_email='karol.marcjan@gmail.com',

        install_requires=[
            'pyglet>=1.1,<2',
            'numpy>=1.8',
            'scipy==0.14'],

        package_dir={'': 'src'},
        packages=find_packages('src'),
        package_data={
            'silica.viz.glass': ['*.glsl'],
            'silica.viz.common': ['*.glsl'],
            'silica.viz.common.grid' : ['surface_inline.c']})
