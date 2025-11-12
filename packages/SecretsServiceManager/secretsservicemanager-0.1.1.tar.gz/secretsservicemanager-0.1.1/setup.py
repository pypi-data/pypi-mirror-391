from setuptools import setup, find_packages

setup(
    name='SecretsServiceManager',
    version='0.1.1',
    author='Antick Mazumder',
    author_email='antick.majumder@gmail.com',
    description='A Python package providing helper function to dynamically retrieve secrets & their values from cloud platforms like Azure or AWS.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/antick-coder/SecretManager-Pkg.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)