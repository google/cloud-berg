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
import logging
import os

from berg import git_util, logger
from berg.configuration import config, BERG_REPO_ROOT
from berg.util import check_call


def cp(src_path, dest_path):
  if logger.level < logging.DEBUG:
    check_call('gsutil -q cp %s %s' % (src_path, dest_path))
  else:
    check_call('gsutil cp %s %s' % (src_path, dest_path))


def rsync(src_dir, dest_dir):
  if logger.level < logging.DEBUG:
    check_call('gsutil -q -m rsync -r %s %s' % (src_dir, dest_dir))
  else:
    check_call('gsutil -m rsync -r %s %s' % (src_dir, dest_dir))


def upload_repo(repo_name):
  rsync(git_util.current_repo_path(),
        os.path.join(config.gcs_repo_root, repo_name))


def upload_berg_repo_for_self_update():
  rsync(BERG_REPO_ROOT, os.path.join(config.gcs_repo_root, 'berg'))


def download_repo(repo_name):
  local_repo = os.path.join('/root/code', repo_name)
  os.makedirs(local_repo, exist_ok=True)
  rsync(os.path.join(config.gcs_repo_root, repo_name), local_repo)
