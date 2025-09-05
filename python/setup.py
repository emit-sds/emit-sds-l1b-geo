from setuptools import setup

# Version moved so we have one place it is defined.
exec(open("emit/version.py").read())

# Namespace packages are a bit on the new side. If you haven't seen
# this before, look at https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages for a description of
# this.
setup(
    name='emit',
    version=__version__,
    description='EMIT',
    author='Mike Smyth, Veljko Jovanovic',
    author_email='mike.m.smyth@jpl.nasa.gov',
    license='Apache 2.0',
    packages=['emit'],
    package_data={"*" : ["py.typed", "*.pyi"]},
    install_requires=[
        'numpy', 'scipy', 
    ],
)
