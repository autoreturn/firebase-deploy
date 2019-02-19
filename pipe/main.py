import colorlog
import os
import sys
import json
import subprocess

from colorama import Fore, Style

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
    commit = os.getenv('BITBUCKET_COMMIT', 'local')
    repo = os.getenv('BITBUCKET_REPO', 'local')
    message = get_variable('MESSAGE', default=f'Deploy {commit} from {repo}')

    args = [
        'firebase',
        'deploy',
         '--token', get_variable('FIREBASE_TOKEN', required=True),
         '--message', message]

    if project is not None:
        args.extend(['--project', project])
    else:
        # get the project id from .firebaserc
        logger.info('Project id not specified, trying to fectch it from .firebaserc')
        data = json.load(open('.firebaserc'))
        project = data['projects']['default']

    logger.info('Starting deployment of the project to firebase')

    result = subprocess.run(args, check=False, capture_output=True)

    if result.returncode != 0:
        fail(message=result.stderr)

    success(f'Successfully deployed project {project}. Project link: https://console.firebase.google.com/project/{project}/overview')


if __name__ == '__main__':
    logger = configure_logger()
    enable_debug()
    run_pipe()
