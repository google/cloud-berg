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
import json
import os
import re
import sys

from berg import logger, gsutil
from berg.configuration import config
from colorama import Fore


def local_path(name):
  return os.path.join(config.local_berg_root, 'jobs',
                      "%s_job_metadata.json" % name)


def gcs_path(name):
  return os.path.join(config.gcs_berg_root, 'jobs',
                      "%s_job_metadata.json" % name)


def parse_local(name, permissive=False):
  try:
    with open(local_path(name), 'r') as f:
      return json.loads(f.read())
  except FileNotFoundError as e:
    if permissive:
      return {}
    else:
      raise e


def save_to_local_path(metadata, name):
  path = local_path(name)
  os.makedirs(os.path.dirname(path), exist_ok=True)
  logger.debug("Wrote metadata to %s" % path)
  with open(path, 'w') as f:
    f.write(json.dumps(metadata, indent=4))


def upload_to_gcs(name):
  gsutil.cp(local_path(name), gcs_path(name))


def upload_copy_to_gcs_results_dir(name, results_dir):
  dest = os.path.join(config.gcs_results_root, results_dir,
                      "berg_job_metadata.json")
  gsutil.cp(local_path(name), dest)


def fetch_and_parse(name):
  path = local_path(name)
  os.makedirs(os.path.dirname(path), exist_ok=True)
  gsutil.cp(gcs_path(name), path)
  return parse_local(name)


def sketchy_guess_at_results_dir_from_cmd(cmd):
  """Try to figure out the results_dir from cmd, if we fail, return '<none>' """
  match = re.search('berg_results/(\S*)', cmd)
  if match is not None and len(match.groups()) == 1:
    return match[1].strip()
  else:
    print(Fore.RED + "Could not guess the results_dir from the command. "
                     "Please specify it explicitly with --results-dir")
    sys.exit(1)
