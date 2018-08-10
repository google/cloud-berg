# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys


py_version = (sys.version_info.major, sys.version_info.minor)
if py_version < (3, 6):
  raise ValueError(
    "This module is only compatible with Python 3.6+, but you are running "
    "Python {}. We recommend installing conda and adding it to your PATH:"
    "https://conda.io/docs/user-guide/install/index.html".format(py_version))

from setuptools import setup
import berg

setup(
  name='berg',
  packages=['berg'],
  version=berg.VERSION,
  install_requires=[
    "click",
    "ipdb",
    'halo ~= 0.0.12',
    'texttable ~= 1.2',
    'colorama ~= 0.3',
    'watchdog ~= 0.8.3',
  ],
  author='Tom B Brown',
  author_email='tombrown@google.com',
  extras_require={
    "test": [
      'pytest ~= 3.2',
    ]
  },
  scripts=[
    'bin/berg',
    'bin/berg-worker',
    'bin/berg-results',
    'bin/berg-self-update',
  ]
)
