import sys
import json
import subprocess

import yaml

from bitbucket_pipes_toolkit import Pipe, get_variable, get_logger


schema = {
    "FIREBASE_TOKEN": {"required": True, "type": "string"},
    "PROJECT_ID": {"required": False, "type": "string", "nullable": True, "default": None},
    "MESSAGE": {"type": "string", "required": False, "nullable": True, "default": None},
    "EXTRA_ARGS": {"type": "string", "required": False, "default": ''},
    "DEBUG": {"type": "boolean", "required": False, "default": False}
}


logger = get_logger()


class FirebaseDeploy(Pipe):

    def run(self):
        super().run()
        logger.info('Executing the pipe...')
        project = self.get_variable('PROJECT_ID')
        token = self.get_variable('FIREBASE_TOKEN')
        message = self.get_variable('MESSAGE')
        extra_args = self.get_variable('EXTRA_ARGS')
        debug = self.get_variable('DEBUG')

        commit = get_variable('BITBUCKET_COMMIT', default='local')
        repo = get_variable('BITBUCKET_REPO_SLUG', default='local')
        workspace = get_variable('BITBUCKET_WORKSPACE', default='local')

        if message is None:
            message = get_variable('MESSAGE', default=f'Deploy {commit} from https://bitbucket.org/{workspace}/{repo}')

        args = [
            'firebase',
            '--token', token,
        ]

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
                                encoding="utf-8",
                                stdout=sys.stdout,
                                stderr=sys.stderr)

        if result.returncode != 0:
            self.fail(message=f'Deployment failed.')

        self.success(f'Successfully deployed project {project}. Project link: https://console.firebase.google.com/project/{project}/overview')


if __name__ == '__main__':
    with open('/usr/bin/pipe.yml', 'r') as metadata_file:
        metadata = yaml.safe_load(metadata_file.read())
    pipe = FirebaseDeploy(pipe_metadata=metadata, schema=schema, check_for_newer_version=True)
    pipe.run()
