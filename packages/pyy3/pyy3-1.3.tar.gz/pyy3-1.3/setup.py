from setuptools import setup, find_packages

setup(
    name='pyy3',
    version='1.3',
    description='Alternative runner for python for the public+export keywords',
    author='Semicolon Studios',
    author_email='fossil.org1@gmail.com',
    install_requires=[],
    packages=find_packages(),
    package_data={
        "pyy": ["pyy/*"]
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pyy=pyy.main:run',
        ],
    },

)
