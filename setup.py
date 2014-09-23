from distutils.core import setup

setup(
        name='silica',
        url='bitbucket.org/szabba/silica_display',
        version='0.1',

        author='Karol Marcjan',
        author_email='karol.marcjan@gmail.com',

        package_dir={'silica': 'src'},
        packages=['silica', 'silica.viz', 'silica.viz.glass'],
        package_data={
            'silica.viz.glass': ['*.glsl', 'glass_inline.c'],
            })
