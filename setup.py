#!/usr/bin/env python

from setuptools import setup, find_packages
import os

#from pip.req import parse_requirements
#import pip
#requirements = [
#    str(req.req) for req in parse_requirements('requirements.txt', session=pip.download.PipSession())
#]

setup(name='maxmind-wrapper',
      version=os.getenv('VERSION'),
      description='Wrapper around Maxmind for automated updates',
      author='Spencer Stirling',
      packages=[
          'maxmind-wrapper',
      ],
      include_package_data=True,
      install_requires=[
          'geoip2',
      ],
     )
