#!/usr/bin/env python


import os

from setuptools import setup
import versioneer


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(name='cmlCiscoSparkSDK',
      description='Pythonic Cisco Spark SDK',
      long_description=read('README.md'),
      keywords='cisco spark api sdk',
      url='https://github.com/cmlccie/cmlCiscoSparkSDK',
      author='Chris Lunsford',
      author_email='chrlunsf@cisco.com',
      license='MIT',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      install_requires=['requests', 'pytz'],
      packages=['cmlCiscoSparkSDK'],
      classifiers=['Development Status :: 3 - Alpha'],
     )
