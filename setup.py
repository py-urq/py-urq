from setuptools import setup, find_packages
from os import path


project_directory = path.abspath(path.dirname(__file__))


def load_from(file_name):
    with open(path.join(project_directory, file_name), encoding='utf-8') as f:
        return f.read()


setup(
    name='py_urq',
    version=load_from('py_urq/py_urq.version').strip(),
    description='URQ quest language parser',
    long_description=load_from('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/py-urq/py-urq',
    author='Kirill Sulim',
    author_email='kirillsulim@gmail.com',
    license='MIT',
    packages=find_packages(include=[
        'py_urq',
    ]),
    package_data={
        'py_urq': [
            'py_urq.version',
        ]
    },
    test_suite='tests',
    install_requires=[
    ],
    classifiers=[
    ],
    keywords='urq quest',
)
