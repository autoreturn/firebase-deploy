import colorlog
import os
import sys
import json
import subprocess

from colorama import Fore, Style

from bitbucket_pipes_toolkit.helpers import *

_debug = False

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
            fail(message='Was not able to find project ID in .firebaserc. Check your configuration.')

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
