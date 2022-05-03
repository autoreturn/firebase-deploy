import os
import sys
import json
import base64
import warnings
import subprocess

import yaml

from bitbucket_pipes_toolkit import Pipe, get_variable


schema = {
    'FIREBASE_TOKEN': {'required': False, 'type': 'string'},
    'KEY_FILE': {'required': False, 'type': 'string'},
    'PROJECT_ID': {'required': False, 'type': 'string', 'nullable': True, 'default': None},
    'MESSAGE': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
    'EXTRA_ARGS': {'type': 'string', 'required': False, 'default': ''},
    'MULTI_SITES_CONFIG': {
        'empty': False,
        'required': False,
        'schema': {
            'type': 'dict',
            'schema': {
                'TARGET': {'type': 'string', 'required': True},
                'RESOURCE': {'type': 'string', 'required': True}
            }
        }},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False}
}


DEFAULT_NODE_JS_VERSION = 12
DEFAULT_FUNCTIONS_DIR_PATH = "./functions"


class FirebaseDeploy(Pipe):

    def run(self):
        super().run()

        self.log_info('Executing the pipe...')
        project = self.get_variable('PROJECT_ID')
        token = self.get_variable('FIREBASE_TOKEN')
        key_file = self.get_variable('KEY_FILE')
        message = self.get_variable('MESSAGE')
        extra_args = self.get_variable('EXTRA_ARGS')
        debug = self.get_variable('DEBUG')

        commit = get_variable('BITBUCKET_COMMIT', default='local')
        repo = get_variable('BITBUCKET_REPO_SLUG', default='local')
        workspace = get_variable('BITBUCKET_WORKSPACE', default='local')

        KEY_FILE_LOCATION = '/tmp/key-file.json'

        # find later a better way to define mutual exclusive (require one of , all of , fields)
        if not (key_file or token):
            self.fail('KEY_FILE or FIREBASE_TOKEN variables should be defined')
        if token:
            warnings.warn("FIREBASE_TOKEN is deprecated due to its legacy. "
                          "For better auth use google service account KEY_FILE", DeprecationWarning)

        nodejs_version = DEFAULT_NODE_JS_VERSION
        # try to find nodejs version, if not - use Default
        # check for alternative path to functions directory
        try:
            with open('firebase.json', 'r') as f:
                data = json.load(f)
                functions_dir_path = data["functions"]["source"]
        except FileNotFoundError:
            pass
        except KeyError:
            pass

        functions_dir_path = DEFAULT_FUNCTIONS_DIR_PATH

        if os.path.isdir(functions_dir_path):
            self.log_info(message=f'Found directory for functions: {functions_dir_path}')
            try:
                with open(f'{functions_dir_path}/package.json', 'r') as f:
                    data = json.load(f)
                    nodejs_version = data["engines"]["node"]
            except FileNotFoundError:
                self.log_warning(message=f'The {functions_dir_path}/package.json file is missing.')
            except json.decoder.JSONDecodeError:
                self.log_warning(message=f'The {functions_dir_path}/package.json file is broken.')
            except KeyError:
                self.log_warning(message='Was not able to find NodeJS version in the functions/package.json.')

        if nodejs_version:
            self.log_info(message="Current NodeJS version:")
            n_result = subprocess.run(['n', str(nodejs_version)],
                                      check=False,
                                      text=True,
                                      encoding='utf-8',
                                      stdout=sys.stdout,
                                      stderr=sys.stderr)

            if n_result.returncode != 0:
                self.log_info(f'{n_result.stderr}')
                self.fail(message=f'Trying to use {nodejs_version} Node JS version failed.')

        if message is None:
            message = get_variable('MESSAGE', default=f'Deploy {commit} from https://bitbucket.org/{workspace}/{repo}')

        args = ['firebase', ]
        if key_file:
            key_content = base64.b64decode(key_file)
            with open(KEY_FILE_LOCATION, 'w') as f:
                f.write(key_content.decode())
            os.putenv('GOOGLE_APPLICATION_CREDENTIALS', KEY_FILE_LOCATION)
        else:
            args.extend(('--token', token))

        if debug:
            args.append('--debug')

        if project is None:
            # get the project id from .firebaserc
            self.log_info('Project id not specified, trying to fectch it from .firebaserc')
            try:
                data = json.load(open('.firebaserc'))
                project = data['projects']['default']
            except FileNotFoundError:
                self.fail(message='.firebaserc file is missing and is required')
            except KeyError:
                self.fail(message='Was not able to find project ID in .firebaserc. Check your configuration.')

        if self.get_variable('MULTI_SITES_CONFIG'):
            # MULTI_SITES = [{'TARGET': 'target name', 'RESOURCE': 'appropriate resource name'}]
            multi_sites = list(self.get_variable('MULTI_SITES_CONFIG'))
            for site in multi_sites:
                target = site['TARGET']
                resource = site['RESOURCE']
                result = subprocess.run(f'firebase target:apply hosting {target} {resource} '
                                        f'--project {project}'.split(),
                                        check=False,
                                        text=True,
                                        encoding='utf-8',
                                        stdout=sys.stdout,
                                        stderr=sys.stderr)
                if result.returncode != 0:
                    self.fail(f'Command target:apply for MULTI_SITES target failed. Error: {sys.stderr}')

        args.extend(['--project', project])
        args.extend(['deploy', '--message', message])

        args.extend(extra_args.split())

        self.log_info('Starting deployment of the project to Firebase.')

        result = subprocess.run(args,
                                check=False,
                                text=True,
                                encoding='utf-8',
                                stdout=sys.stdout,
                                stderr=sys.stderr)

        if result.returncode != 0:
            self.fail(message='Deployment failed.')

        self.success(f'Successfully deployed project {project}. '
                     f'Project link: https://console.firebase.google.com/project/{project}/overview')


if __name__ == '__main__':
    with open('/pipe.yml', 'r') as metadata_file:
        metadata = yaml.safe_load(metadata_file.read())
    pipe = FirebaseDeploy(pipe_metadata=metadata, schema=schema, check_for_newer_version=True)
    pipe.run()
