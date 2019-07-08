import os
import subprocess
import datetime

import requests


docker_image = 'bitbucketpipelines/demo-pipe-python:ci' + os.getenv('BITBUCKET_BUILD_NUMBER', 'local')


def docker_build():
  """
  Build the docker image for tests.
  :return:
  """
  args = [
    'docker',
    'build',
    '-t',
    docker_image,
    '.',
  ]
  subprocess.run(args, check=True)


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
public_project_url = 'https://pipes-ci.firebaseapp.com/'


def setup_module():
  path = os.path.join(os.path.dirname(__file__), '.firebaseapp/public/index.html')
  with open(path, 'w') as index:
    global now
    now = datetime.datetime.now().isoformat()
    index.write(index_template.format(dt=now))
  docker_build()


def test_no_parameters():
  args = [
    'docker',
    'run',
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 1
  assert 'FIREBASE_TOKEN variable missing.' in result.stderr


def test_project_deployed_successfully():
  working_dir = os.path.join(os.getcwd(), 'test', '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 0
  assert 'Successfully deployed project' in result.stdout

  response = requests.get(public_project_url)

  assert now in response.text


def test_success_with_project_id():
  working_dir = os.path.join(os.getcwd(), 'test', '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-e', f'PROJECT=pipes-prod',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 0
  assert 'Successfully deployed project' in result.stdout


def test_success_extra_args():
  working_dir = os.path.join(os.getcwd(), 'test', '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-e', f'EXTRA_ARGS=--only hosting',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 0
  assert 'Successfully deployed project' in result.stdout


def test_success_debug():
  working_dir = os.path.join(os.getcwd(), 'test', '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-e', f'DEBUG=true',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 0
  assert 'Successfully deployed project' in result.stdout


def test_subprocess_streams_output():
  working_dir = os.path.join(os.getcwd(), 'test', '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 0
  assert 'Deploy complete!' in result.stdout


def test_deploy_failed():
  working_dir = os.path.join(os.getcwd(), 'test', '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-e', f'EXTRA_ARGS=--only hosting:target-name-not-exist',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  assert result.returncode == 1
  assert 'Deployment failed' in result.stdout
