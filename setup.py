from setuptools import setup

setup(
    name='nginx-parser',
    packages=['src'],
    version='0.1',
    description='A simple parser for nginx logs',
    author='George Davaris',
    author_email='davarisg@gmail.com',
    license='MIT',
    url='https://github.com/davarisg/nginx-parser',  # use the URL to the github repo
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=['blessed>=1.14.2', 'PyYAML>=3.12'],
    entry_points={
        'console_scripts': [
            'nginx-parser=src.parser:main',
        ],
    },
)
