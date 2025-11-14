from setuptools import setup, find_packages

setup(
    name='asb_cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points='''
        [console_scripts]
        asb_cli=asb_cli.cli:main
    ''',
    author='hjl',
    author_email='hjl@hjl.com',
    description='A CLI tool for managing Ansible projects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hujianli94/asb_cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
)
