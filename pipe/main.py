import colorlog
import os
import sys
import json
import subprocess

from colorama import Fore, Style

_debug = False

def configure_logger():
  handler = colorlog.StreamHandler()
  handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s: %(message)s'))
  logger = colorlog.getLogger('root')
  logger.addHandler(handler)
  logger.setLevel('INFO')
  return logger

def get_variable(name, required=False, default=None):
  """
  Fetch the value of a pipe variable.
  :param name: Variable name.
  :param required: Throw an exception if the env var is unset.
  :param default: Default value if the env var is unset.
  :return:
  """
  value = os.getenv(name)
  if required and (value == None or not value.strip()):
    raise Exception('{} variable missing.'.format(name))
  return value if value else default

def enable_debug():
  debug = get_variable('DEBUG', required=False, default="False").lower()
  if debug == 'true':
    logger.info('Enabling debug mode.')
    global _debug
    _debug = True
    logger.setLevel('DEBUG')

def success(message='Success'):
  print('{}✔ {}{}'.format(Fore.GREEN, message, Style.RESET_ALL))
  sys.exit(0)

def fail(message='Fail!'):
  print('{}✖ {}{}'.format(Fore.RED, message, Style.RESET_ALL))
  sys.exit(1)

def run_pipe():
    logger.info('Executing the pipe...')
    project = get_variable('PROJECT_ID')
    commit = get_variable('BITBUCKET_COMMIT', default='local')
    repo = get_variable('BITBUCKET_REPO_SLUG', default='local')
    account = get_variable('BITBUCKET_REPO_OWNER', default='local')
    message = get_variable('MESSAGE', default=f'Deploy {commit} from https://bitbucket.org/{account}/{repo}')

    args = [
        'firebase',
        '--token', get_variable('FIREBASE_TOKEN', required=True),
    ]

    if _debug:
        args.append('--debug')

    if project is None:
        # get the project id from .firebaserc
        logger.info('Project id not specified, trying to fectch it from .firebaserc')
        try:
            data = json.load(open('.firebaserc'))
            project = data['projects']['default']
        except FileNotFoundError as e:
            fail(message='.firebaserc file is missing and is required')
        except KeyError as e:
            fail(message='Was no able to find project ID in .firebaserc. Check your configuration.')

    args.extend(['--project', project])
    args.extend(['deploy', '--message', message])

    args.extend(get_variable('EXTRA_ARGS', default='').split())

    logger.info('Starting deployment of the project to Firebase.')

    result = subprocess.run(args, check=False, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        fail(message=result.stderr.strip())

    success(f'Successfully deployed project {project}. Project link: https://console.firebase.google.com/project/{project}/overview')


if __name__ == '__main__':
    logger = configure_logger()
    enable_debug()
    run_pipe()
