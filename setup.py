#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.1'

setup(name='python-csp',
      version=version,
      description="Communicating sequential processes for Python",
      long_description="""\
python-csp adds communicating sequential processes to Python""",
      classifiers=["Intended Audience :: Developers",
                   ("License :: OSI Approved :: " +
                    "GNU General Public License (GPL)"),
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: System :: Distributed Computing"],
      keywords='concurrency multicore parallel',
      author='Sarah Mount',
      author_email='s.mount@wlv.ac.uk',
      url='http://github.com/snim2/python-csp/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test',
                                      'benchmark', 'rst', 'scripts', ]),
      include_package_data=True,
      zip_safe=True,
      scripts=['scripts/python-csp', ],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
