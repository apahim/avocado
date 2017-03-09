#!/bin/env python
import os
from setuptools import setup, find_packages


root_path = os.path.abspath(os.path.join("..", ".."))
version_file = os.path.join(root_path, 'VERSION')
VERSION = open(version_file, 'r').read().strip()

setup(name='avocado-myrun',
      description='Avocado MyRun',
      version=VERSION,
      author='Avocado Developers',
      author_email='avocado-devel@redhat.com',
      url='http://avocado-framework.github.io/',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[],
      entry_points={
          'avocado.plugins.cli.cmd': [
              'run = avocado_myrun:Run',
          ]}
      )
