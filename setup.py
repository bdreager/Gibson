#!/usr/bin/env python
# -*- coding: utf-8 -*-

try: from setuptools import setup
except ImportError: from distutils.core import setup

script_name = 'gibson.py'
classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console :: Curses',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    #'Programming Language :: Python :: 3', #TODO test this
    'Topic :: Terminals',
    'Topic :: Artistic Software'
]
keywords=['terminal', 'hacking', 'animation','ascii', 'art', 'ncurses']

with open(script_name) as f:
    meta = dict(
        (k.strip(' _'), eval(v)) for k, v in
        (line.split('=') for line in f if line.startswith('__'))
    )

    meta_renames = [
        ('program', 'name'),
        ('website', 'url'),
        ('email', 'author_email'),
    ]
    for old, new in meta_renames:
        if old in meta:
            meta[new] = meta[old]
            del meta[old]

    meta_keys = ['name', 'description', 'version', 'license', 'url', 'author', 'author_email']
    meta = dict([m for m in meta.items() if m[0] in meta_keys])

setup_d = dict(
    long_description=open('README.rst').read(),
    classifiers=classifiers,
    scripts=[script_name],
    keywords=keywords,
    entry_points={'console_scripts': ['gibson=gibson:main']},
    packages=[''],

    **meta
)

if __name__ == '__main__':
    setup(**setup_d)
