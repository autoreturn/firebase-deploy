import colorlog
import os
import sys

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
  name = get_variable('NAME', required=True)
  success(message=name)

logger = configure_logger()
enable_debug()
run_pipe()
