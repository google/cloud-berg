# -*- coding: utf-8 -*-from __future__ import unicode_literals
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
import subprocess
import sys

import berg
import click
from berg import util
from berg.util import check_output, spinner, BergException
from colorama import Fore

BERG_REPO_ROOT = os.path.dirname(os.path.dirname(__file__))


class Config():
  """Utility object that holds our global constants"""
  local_berg_root = os.path.expanduser('~/.berg/')
  instance_results_root = '/root/berg_results'

  # These instance creation config values must be initialized from local file
  default_image = None
  default_image_project = None

  def _stored_config(self):
    try:
      with open(self.config_file, 'r') as f:
        return json.load(f)

    except (FileNotFoundError):
      return {}

  @property
  def bucket(self):
    bucket = self._stored_config().get('bucket')
    if not bucket:
      raise BergException("No bucket found in ~/.berg/berg.json. Run berg init")
    return bucket

  @property
  def service_account(self):
    return self._stored_config()['service_account']

  @property
  def config_file(self):
    return os.path.join(self.local_berg_root, 'berg.json')

  @property
  def gcs_berg_root(self):
    return os.path.join(self.bucket, '.berg/')

  @property
  def gcs_repo_root(self):
    return os.path.join(self.gcs_berg_root, 'repos')

  @property
  def gcs_results_root(self):
    return os.path.join(self.bucket, 'berg_results')

  def initialize_with_bucket(self, bucket):
    stored_config = {
      'bucket': bucket,
      '_version': berg.VERSION,
    }
    self.write_config(stored_config)

  def write_config(self, stored_config):
    os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
    with open(self.config_file, 'w') as f:
      f.write(json.dumps(stored_config, indent=4))

  def initialize_for_creating_instances(self, force_walkthrough=False):
    """
    We need a few manually entered values before running instances. This
    is only needed for `berg run`

    :param force_walkthrough: Do the walkthrough and healthchecks
    """
    if force_walkthrough:
      stored_config = self._first_time_setup_walkthrough()
    else:
      stored_config = self._stored_config()
      if not 'bucket' in stored_config:
        stored_config = self._first_time_setup_walkthrough()

    self.default_image = stored_config['default_image']
    self.default_image_project = stored_config['default_image_project']

  def _first_time_setup_walkthrough(self):
    stored_config = {
      'default_image': 'berg-0-0-21-cuda-9-tf-1-8-0-torch-0-4-0-mpi',
      'default_image_project': 'cloud-berg',
      '_version': berg.VERSION,
    }
    print(f"\nHi! 👋  Welcome to berg. Let's do a quick setup:{Fore.WHITE}")

    if check_output('which gcloud'):
      print(f"1.{Fore.GREEN} Found installation of gcloud.{Fore.WHITE}")
    else:
      print(f"{Fore.RED}gcloud not installed, install it by following the \
directions here: https://cloud.google.com/sdk/downloads{Fore.WHITE}")
      sys.exit(1)

    with spinner("Installing gcloud beta"):
      check_output("yes | gcloud components install beta")
    print(f"2.{Fore.GREEN} gcloud beta is up to date.{Fore.WHITE}")

    with spinner("Fetching service account"):
      service_acct = check_output(
        "gcloud iam service-accounts list --format 'csv(EMAIL)'").split('\n')[1]
    print(f"3.{Fore.GREEN} Found service account {service_acct}{Fore.WHITE}")
    stored_config['service_account'] = service_acct

    if check_output('which gsutil'):
      print(f"4.{Fore.GREEN} Found installation of gsutil.{Fore.WHITE}")
    else:
      print(
        Fore.RED + "gsutil not installed, install it by following the directions"
                   " here: https://cloud.google.com/sdk/downloads{Fore.WHITE}")
      sys.exit(1)

    with spinner(f"Fetching default project"):
      project = check_output("gcloud config get-value project")
      stored_config['project'] = project
    print(f"5.{Fore.GREEN} Using default project [{project}].{Fore.WHITE}")

    img_proj = stored_config['default_image_project']
    try:
      with spinner(f"Checking access to default image project [{img_proj}]"):
        check_output(f'gcloud compute images list --project {img_proj}',
                     catch_errors=False)
    except subprocess.CalledProcessError:
      print(Fore.RED + (
        f"Image project [{img_proj}] is not accessible. \n" +
        "Join http://g/brain-on-cloud to gain access to the project"))
      sys.exit(1)

    print(f"6.{Fore.GREEN} Golden image project [{img_proj}] \
is accessible.{Fore.WHITE}")

    try:
      print(f"7.{Fore.GREEN} Using bucket {self.bucket}")
      stored_config['bucket'] = self.bucket
    except BergException:
      print(f"7.{Fore.YELLOW} No bucket set in {self.config_file}{Fore.WHITE}")
      stored_config['bucket'] = click.prompt(
        "\nEnter a bucket to store berg results in (e.g. "
        "gs://<my_ldap>-experiments). If you don't have a bucket you can create "
        "one with `gsutil mb gs://<my_bucket_name>>` and then enter it here",
        type=str)

    self.write_config(stored_config)
    print(f"\nWrote config to {self.config_file}")
    util.pretty_print_dict(self.config_file, stored_config)

    return stored_config  # Global object that holds our config


config = Config()
