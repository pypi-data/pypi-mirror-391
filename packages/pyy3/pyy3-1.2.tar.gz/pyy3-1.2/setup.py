from setuptools import setup, find_packages

setup(
    name='pyy3',
    version='1.2',
    description='Alternative runner for python for the public+export keywords',
    author='Semicolon Studios',
    author_email='fossil.org1@gmail.com',
    install_requires=[],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyy=pyy.main:run',
        ],
    },

)
