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
import random
import string
import subprocess
import sys
import time

from berg import logger
from colorama import Fore
from halo import Halo
from texttable import Texttable
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO


class BergException(Exception):
  pass


def check_call(command, permissive=False, **kwargs):
  """Execute a command and return True if it completed successfully. """
  logger.debug("Running command: %s" % command)

  try:
    subprocess.check_call(command, shell=True, **kwargs)
    return True
  except subprocess.CalledProcessError as e:
    if permissive:
      return False
    else:
      raise e


def check_output(command, catch_errors=True):
  """Execute a command and return the output as a stripped string. """
  try:
    return subprocess.check_output(
      command, shell=True,
      stderr=subprocess.STDOUT).decode('utf-8').strip()
  except subprocess.CalledProcessError as suberror:
    if catch_errors:
      print("\n" + Fore.RED + suberror.stdout.decode('utf-8'))
      sys.exit(1)
    else:
      raise suberror


def random_alphanum(length):
  alphanum = string.ascii_lowercase + string.digits
  return "".join([random.choice(alphanum) for _ in range(length)])


def spinner(text):
  """Default halo spinner style"""
  return Halo(text=text, spinner='dots')


def pretty_print_cmd(title, string):
  _pretty_print(title, Fore.CYAN + string)


def _pretty_print(title, string):
  title = '\n========= %s =========' % title
  print(title)
  print(string)
  print("=" * len(title) + '\n')


def pretty_table(header):
  """Return a Texttable object that matches the gcloud table output style"""
  table = Texttable(max_width=0)  # No max width
  table.set_deco(Texttable.HEADER)
  table.add_row(header)
  return table


def pretty_print_dict(title, metadata):
  colored_metadata = ""
  for k, v in metadata.items():
    colored_metadata += Fore.WHITE + str(k) + ": "
    colored_metadata += Fore.CYAN + str(v) + "\n"
  _pretty_print(title, colored_metadata.strip())


def pretty_print_metadata(title, metadata):
  md = metadata.copy()
  if md['git_patch']:
    # Pretty print the patch
    git_patch_lines = metadata['git_patch'].split('\n')
    md['git_patch'] = "\n".join(
      git_patch_lines[:4]) + Fore.WHITE + \
                      "\n             ...    " + Fore.YELLOW + \
                      "\n    [plus %s additional git_patch lines]" % \
                      len(git_patch_lines[4:]) + Fore.WHITE
  else:
    md['git_patch'] = "<none>"
  pretty_print_dict(title, md)


def watch_dir_and_run_fn(dir, fn):
  """Recursively watch a directory and run a function upon changes"""

  class EventHandler(RegexMatchingEventHandler):
    def __init__(self):
      super(EventHandler, self).__init__(ignore_regexes=[
        ".*/\.git.*", '.*/\.idea.*',
      ])

    def on_modified(self, event):
      logger.debug(event)
      fn()

  event_handler = EventHandler()
  observer = Observer()
  observer.schedule(event_handler, dir, recursive=True)
  observer.start()
  try:
    while True:
      time.sleep(0.1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
