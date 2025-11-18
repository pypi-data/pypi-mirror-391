from setuptools import setup, find_packages

setup(
    name='pydbinterface',
    version='0.0.0',
    description='Interfaz sencilla para conectar y manipular bases de datos en Python',
    author='darth wayne',
    author_email='darrthwayne@gmail.com',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
