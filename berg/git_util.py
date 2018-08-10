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
import os
import subprocess
import sys

from berg.util import check_output
from colorama import Fore


def output(cmd):
  """Run a git command and report an error if it fails"""
  try:
    return check_output(cmd, catch_errors=False)
  except subprocess.CalledProcessError:
    print(Fore.RED + "This berg command must be called from within a git repo")
    sys.exit(1)


def is_dirty():
  return bool(output('git diff HEAD'))


def current_commit():
  return output('git rev-parse --short HEAD')


def complain_if_dirty_git(allow_dirty_git):
  if not allow_dirty_git and is_dirty():
    print(Fore.RED +
          "There are uncommitted changes in the current repository. "
          "Commit your changes to get a reproducible experiment. If you'd "
          "like your workers to ignore commits, run your command with "
          "--allow-dirty-git.")
    sys.exit(1)


def current_repo_path():
  return output("git rev-parse --show-toplevel")


def current_repo_name():
  return os.path.basename(current_repo_path())


def write_temp_patchfile(patch, name):
  t_file_path = os.path.join('/tmp', name + "_patch")
  with open(t_file_path, 'w') as t_file:
    t_file.write(patch.strip() + '\n')

  return t_file_path
