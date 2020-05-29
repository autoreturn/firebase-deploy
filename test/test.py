import os
import datetime

import requests

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

        self.assertRegex(result, 'FIREBASE_TOKEN:\n- required field')

    def test_project_deployed_successfully(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN")
        })

        self.assertRegex(result, 'Successfully deployed project')

        response = requests.get(public_project_url)

        self.assertIn(now, response.text)

    def test_success_with_project_id(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN"),
            'PROJECT': 'pipes-prod'
        })

        self.assertRegex(result, 'Successfully deployed project')

    def test_success_extra_args(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN"),
            'EXTRA_ARGS': '--only hosting'
        })

        self.assertRegex(result, 'Successfully deployed project')

    def test_success_debug(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN"),
            'DEBUG': 'true'
        })

        self.assertRegex(result, 'Successfully deployed project')

    def test_subprocess_streams_output(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN"),
            'EXTRA_ARGS': '--only hosting'
        })

        self.assertRegex(result, 'Successfully deployed project')

        self.assertIn('Deploy complete!', result)

    def test_deploy_failed(self):
        result = self.run_container(environment={
            'FIREBASE_TOKEN': os.getenv("FIREBASE_TOKEN"),
            'EXTRA_ARGS': '--only hosting:target-name-not-exist'
        })

        self.assertIn('Deployment failed', result)
        self.assertIn('Error:', result)
