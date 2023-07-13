#!/usr/bin/env python

import multiprocessing
import os
import re

from setuptools import setup

extra = {}
try:
    from Cython.Build import cythonize

    p = os.path.join("src", "wheezy", "core")
    extra["ext_modules"] = cythonize(
        [os.path.join(p, "*.py")],
        exclude=os.path.join(p, "__init__.py"),
        # https://github.com/cython/cython/issues/3262
        nthreads=0 if multiprocessing.get_start_method() == "spawn" else 2,
        compiler_directives={"language_level": 3},
        quiet=True,
    )
except ImportError:
    pass

try:
    import uuid  # noqa
except ImportError:
    extra["install_requires"] = ["uuid"]

README = open(os.path.join(os.path.dirname(__file__), "README.md")).read()
VERSION = (
    re.search(
        r'__version__ = "(.+)"',
        open("src/wheezy/core/__init__.py").read(),
    )
    .group(1)
    .strip()
)

setup(
    name="wheezy.core",
    version=VERSION,
    python_requires=">=3.8",
    description="A lightweight core library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/akornatskyy/wheezy.core",
    author="Andriy Kornatskyy",
    author_email="andriy.kornatskyy@live.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Software Development :: Localization",
        "Topic :: System :: Benchmark",
    ],
    keywords="core benchmark collections config datetime db descriptor "
    "feistel i18n introspection json luhn mail pooling url uuid",
    packages=["wheezy", "wheezy.core"],
    package_dir={"": "src"},
    namespace_packages=["wheezy"],
    zip_safe=False,
    platforms="any",
    **extra
)
