# Bitbucket Pipelines Pipe: Firebase deploy

Deploy your code to [Firebase](https://firebase.google.com/).

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: atlassian/firebase-deploy:0.3.6
  variables:
    FIREBASE_TOKEN: '<string>'
    # PROJECT_ID: '<string>' # Optional.
    # MESSAGE: '<string>' # Optional.
    # EXTRA_ARGS: '<string>' # Optional.
    # DEBUG: '<boolean>' # Optional.
```
## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| FIREBASE_TOKEN (*)    | Firebase API key |
| PROJECT_ID            | Firebase project ID. Default: `default` (the pipe will use **.firebaserc** file to get the default project id.   |
| MESSAGE               | Deployment message. Default: `Deploy ${BITBUCKET_COMMIT} from https://bitbucket.org/${BITBUCKET_WORKSPACE}/${BITBUCKET_REPO_SLUG}` |
| EXTRA_ARGS            | Extra arguments to be passed to the Firebase CLI (see Firebase docs for more details). Default: `'`.
| DEBUG                 | Turn on extra debug information. Default: `false`. |

_(*) = required variable._

## Details
This pipe deploys code and assets from your project directory to your Firebase project. 
For Firebase Hosting, a firebase.json configuration file is required.

## Prerequisites

You are going to need to install the Firebase CLI and generate an authentication token for use in non-interactive environments.

* [Installing the Firebase CLI](https://firebase.google.com/docs/cli/#install_the_firebase_cli)
* You'll need to use `login:ci` command to generate an authentication token. See the [command reference](https://firebase.google.com/docs/cli/#administrative_commands).

## Examples

Basic example:

```yaml
script:
  - pipe: atlassian/firebase-deploy:0.3.6
    variables:
      FIREBASE_TOKEN: $FIREBASE_TOKEN
```

Advanced example:

```yaml
script:
  - pipe: atlassian/firebase-deploy:0.3.6
    variables:
      FIREBASE_TOKEN: $FIREBASE_TOKEN
      PROJECT_ID: 'myAwesomeProject'
      MESSAGE: 'Deploying myAwesomeProject'
      EXTRA_ARGS: '--only functions'
      DEBUG: 'true'
```

## Support
If you’d like help with this pipe, or you have an issue or feature request, [let us know on Community](https://community.atlassian.com/t5/forums/postpage/choose-node/true/interaction-style/qanda?add-tags=bitbucket-pipelines,pipes,deployment,firebase).

If you’re reporting an issue, please include:

- the version of the pipe
- relevant logs and error messages
- steps to reproduce

## License
Copyright (c) 2018 Atlassian and others.
Apache 2.0 licensed, see [LICENSE.txt](LICENSE.txt) file.
