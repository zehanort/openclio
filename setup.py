try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name =                          'openclio',
    version =                       '0.1',
    description =                   'OpenCL Input/Output',
    long_description =              open('README.md', 'r').read(),
    long_description_content_type = 'text/markdown',
    author =       'Sotiris Niarchos',
    author_email = 'sot.niarchos@gmail.com',
    url =          'https://github.com/zehanort/openclio',
    download_url = 'https://github.com/zehanort/openclio/releases',
    license =      'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    install_requires = ['llvmlite>=0.36.0', 'pandas>=1.2.4', 'tabulate>=0.8.9'],
    python_requires =  '>=3.6',
    entry_points =     { 'console_scripts': ['openclio=openclio.openclio:run'] },
    packages =         ['openclio', 'openclio.utils']
)
