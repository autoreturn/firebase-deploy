import base64
import json
import os
import subprocess
import sys
import yaml
import warnings

from bitbucket_pipes_toolkit import Pipe, get_variable, get_logger


schema = {
    'FIREBASE_TOKEN': {'required': False, 'type': 'string'},
    'KEY_FILE': {'required': False, 'type': 'string'},
    'PROJECT_ID': {'required': False, 'type': 'string', 'nullable': True, 'default': None},
    'MESSAGE': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
    'EXTRA_ARGS': {'type': 'string', 'required': False, 'default': ''},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False}
}


logger = get_logger()


class FirebaseDeploy(Pipe):

    def run(self):
        super().run()

        logger.info('Executing the pipe...')
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
            logger.info('Project id not specified, trying to fectch it from .firebaserc')
            try:
                data = json.load(open('.firebaserc'))
                project = data['projects']['default']
            except FileNotFoundError:
                self.fail(message='.firebaserc file is missing and is required')
            except KeyError:
                self.fail(message='Was not able to find project ID in .firebaserc. Check your configuration.')

        args.extend(['--project', project])
        args.extend(['deploy', '--message', message])

        args.extend(extra_args.split())

        logger.info('Starting deployment of the project to Firebase.')

        result = subprocess.run(args,
                                check=False,
                                text=True,
                                encoding='utf-8',
                                stdout=sys.stdout,
                                stderr=sys.stderr)

        if result.returncode != 0:
            self.fail(message=f'Deployment failed.')

        self.success(f'Successfully deployed project {project}. '
                     f'Project link: https://console.firebase.google.com/project/{project}/overview')


if __name__ == '__main__':
    with open('/usr/bin/pipe.yml', 'r') as metadata_file:
        metadata = yaml.safe_load(metadata_file.read())
    pipe = FirebaseDeploy(pipe_metadata=metadata, schema=schema, check_for_newer_version=True)
    pipe.run()
