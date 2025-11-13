import os
import setuptools
import sys
sys.path.append(os.path.abspath('copr'))
from __info__ import *

with open('./readme.md') as file:
  readme = file.read()

setuptools.setup(
  name='copr.py',
  packages=setuptools.find_packages(),
  include_package_data=True,
  install_requires=[
    'jmespath',
    'requests',
  ],
  extras_require={
    'publish': [
      'twine',
    ],
    'test': [
      'pytest',
      'pytest-sugar',
    ],
  },
  version=pkgVersion,
  author=pkgAuthorsLong,
  author_email=pkgAuthorsEmail,
  description='A library to access the ' + pkgNameAndAcronym,
  long_description=readme,
  long_description_content_type='text/markdown',
  license=pkgLicense.replace(' ', '-'),
  url=pkgUrl,
  keywords=pkgKeywords,
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 3',
  ],
)
