from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='sphinx-timetravel',
    version='0.1.1',
    description='Sphinx plugin for displaying interactive timelines with year/month resolution',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Robbi Nespu',
    author_email='robbinespu@gmail.com',
    url='https://github.com/robbinespu/sphinx-timetravel',
    project_urls={
        'Documentation': 'https://github.com/robbinespu/sphinx-timetravel#readme',
        'Source Code': 'https://github.com/robbinespu/sphinx-timetravel',
        'Bug Tracker': 'https://github.com/robbinespu/sphinx-timetravel/issues',
    },
    packages=find_packages(),
    package_data={
        'sphinx_timetravel': ['_static/timeline.css'],
    },
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'Sphinx>=4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'sphinx-rtd-theme',
        ],
    },
    entry_points={
        'sphinx.extensions': [
            'sphinx_timetravel = sphinx_timetravel:setup',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Documentation',
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Extension',
    ],
    keywords='sphinx documentation timeline visualization',
)
