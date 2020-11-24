import datetime
import json
import os

import pytest
import requests
import shutil
from unittest import mock

from bitbucket_pipes_toolkit.test import PipeTestCase


index_template = """
<html>
  <head>
    <title>Bitbucket Pipelines</title>
  </head>
  <body>
      <p>{dt}</p>
  </body>
</html>
"""

now = None

public_project_url = f"https://{os.getenv('FIREBASE_TEST_PROJECT_NAME')}.firebaseapp.com/"


def setup():
    path = os.path.join(os.path.dirname(__file__), '.firebaseapp/public/index.html')
    with open(path, 'w') as index:
        global now
        now = datetime.datetime.now().isoformat()
        index.write(index_template.format(dt=now))

    project = os.getenv('FIREBASE_TEST_PROJECT_NAME', 'bbci-pipes-test-infra')
    firebase_rc = {'projects': {'default': project, 'production': project}}

    firebase_rc_path = os.path.join(os.path.dirname(__file__), '.firebaseapp/.firebaserc')
    with open(firebase_rc_path, 'w') as f:
        json.dump(firebase_rc, f)


class FirebaseDeployTestCase(PipeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup()

    def setUp(self):
        os.chdir('test/.firebaseapp')

    def tearDown(self):
        os.chdir('../..')

    def test_no_parameters(self):
        result = self.run_container()

        self.assertRegex(result, 'KEY_FILE or FIREBASE_TOKEN variables should be defined')

    def test_project_deployed_successfully(self):
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE')
        })

        self.assertRegex(result, 'Successfully deployed project')
        response = requests.get(public_project_url)

        self.assertIn(now, response.text)

    def test_success_with_project_id(self):
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'PROJECT': 'pipes-prod'
        })

        self.assertRegex(result, 'Successfully deployed project')

    def test_success_extra_args(self):
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'EXTRA_ARGS': '--only hosting'
        })

        self.assertRegex(result, 'Successfully deployed project')

    def test_success_debug(self):
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'DEBUG': 'true'
        })

        self.assertRegex(result, 'Successfully deployed project')

    def test_subprocess_streams_output(self):
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'EXTRA_ARGS': '--only hosting'
        })

        self.assertRegex(result, 'Successfully deployed project')

        self.assertIn('Deploy complete!', result)

    def test_deploy_failed(self):
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'EXTRA_ARGS': '--only hosting:target-name-not-exist'
        })
        self.assertIn('Deployment failed', result)
        self.assertIn('Error:', result)

    @mock.patch.dict(os.environ, {'FIREBASE_TOKEN': 'testtoken'})
    def test_deploy_failed_not_valid_firebase_token(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN"),
        })
        self.assertIn('DeprecationWarning: FIREBASE_TOKEN is deprecated due to its legacy. '
                      'For better auth use google service account KEY_FILE', result)
        self.assertIn('Deployment failed', result)

    @pytest.mark.run(order=-1)
    def test_deploy_multi_target(self):
        shutil.copyfile('firebase.json', '/tmp/firebase.json')
        shutil.copyfile('firebase-multi-site.json', 'firebase.json')

        multi_sites = '''
        [
            {"TARGET": "blog-bbci-pipes-test-infra", "RESOURCE": "blog-bbci-pipes-test-infra"}
        ]
        '''
        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'EXTRA_ARGS': '--only hosting:blog-bbci-pipes-test-infra',
            'MULTI_SITES_CONFIG': multi_sites
        })
        self.assertRegex(result, 'Successfully deployed project')

        result = self.run_container(environment={
            'KEY_FILE': os.getenv('KEY_FILE'),
            'MULTI_SITES_CONFIG': '''
                [
                    {"TARGET": "blog-bbci-pipes-test-infra", "RESOURCE": "blog-bbci-pipes-test-infra"},
                    {"TARGET": "bbci-pipes-test-infra", "RESOURCE": "bbci-pipes-test-infra"}
                ]
        '''
        })
        self.assertRegex(result, 'Successfully deployed project')

        shutil.copyfile('/tmp/firebase.json', 'firebase.json')
