import os
import subprocess

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


def setup_module():
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

def test_success():
  working_dir = os.path.join(os.getcwd(), '.firebaseapp')
  args = [
    'docker',
    'run',
    '-e', f'FIREBASE_TOKEN={os.getenv("FIREBASE_TOKEN")}',
    '-v', f'{working_dir}:{working_dir}',
    '-w', working_dir,
    docker_image,
  ]

  result = subprocess.run(args, check=False, text=True, capture_output=True)
  import pdb;pdb.set_trace()
  assert result.returncode == 0
  assert 'Successfully deployed project' in result.stdout
  

def test_success_extra_args():
  working_dir = os.path.join(os.getcwd(), '.firebaseapp')
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

