# Bitbucket Pipelines Pipe: Firebase deploy

Deploy your code to [Firebase](https://firebase.google.com/).

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: atlassian/firebase-deploy:2.0.0-1
  variables:
    KEY_FILE: '<string>'
    FIREBASE_TOKEN: '<string>'
    # PROJECT_ID: '<string>' # Optional.
    # MESSAGE: '<string>' # Optional.
    # EXTRA_ARGS: '<string>' # Optional.
    # MULTI_SITES_CONFIG: '<json>' # Optional
    # DEBUG: '<boolean>' # Optional.
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| KEY_FILE              | base64 encoded content of Key file for a [Google service account][Google service account]. To encode this content, follow [encode private key docs][encode private key docs].|
| FIREBASE_TOKEN        | Firebase API key. Deprecated: recommended to use KEY_FILE variable|
| PROJECT_ID            | Firebase project ID. Default: `default` (the pipe will use **.firebaserc** file to get the default project id.   |
| MESSAGE               | Deployment message. Default: `Deploy ${BITBUCKET_COMMIT} from https://bitbucket.org/${BITBUCKET_WORKSPACE}/${BITBUCKET_REPO_SLUG}` |
| EXTRA_ARGS            | Extra arguments to be passed to the Firebase CLI (see Firebase docs for more details). Default: `'`.
| MULTI_SITES_CONFIG    | JSON document: list of dictionaries containing mapping TARGET to RESOURCE(s). Provide targets defined in your firebase.json. See how to configure firebase.json in [firebase doc][firebase doc]|
| DEBUG                 | Turn on extra debug information. Default: `false`. |

_(*) = required variable._

## Details
This pipe deploys code and assets from your project directory to your Firebase project. 
For Firebase Hosting, a firebase.json configuration file is required.

NodeJS environment:

For [NodeJS][NodeJS] environment pipe uses version 16 LTS by default. Supported LTS 14 and 12, 10, 8 versions.
The version provided for the `engines` field of the `package.json` file in your `functions/` directory will be used as NodeJS version inside pipe's docker container. See more details in the [Firebase runtime setup docs][Firebase runtime].


** Note! You must provide the same NodeJS version for an docker image in your `bitbucket-pipelines.yml` file as in your `package.json` file. **


## Prerequisites

You are going to need to install the Firebase CLI and generate an authentication token for use in non-interactive environments.

* [Installing the Firebase CLI][Installing the Firebase CLI]
* You'll need to use `login:ci` command to generate an authentication token. See the [command reference][command reference].

## Examples

### Basic example:

```yaml
script:
  - pipe: atlassian/firebase-deploy:2.0.0
    variables:
      KEY_FILE: $KEY_FILE
```

### Advanced example:

Specify additional parameters in the following manner. This can be used, for instance, to explicitly point to project to be deployed.

```yaml
script:
  - pipe: atlassian/firebase-deploy:2.0.0
    variables:
      KEY_FILE: $KEY_FILE
      PROJECT_ID: 'myAwesomeProject'
      MESSAGE: 'Deploying myAwesomeProject'
      EXTRA_ARGS: '--only functions'
      DEBUG: 'true'
```

If you still use legacy FIREBASE_TOKEN approach, we saved this approach to be backward compatible. You can specify parameters in following manners:

```yaml
script:
  - pipe: atlassian/firebase-deploy:2.0.0
    variables:
      FIREBASE_TOKEN: $FIREBASE_TOKEN
```


```yaml
script:
  - pipe: atlassian/firebase-deploy:2.0.0
    variables:
      FIREBASE_TOKEN: $FIREBASE_TOKEN
      PROJECT_ID: 'myAwesomeProject'
      MESSAGE: 'Deploying myAwesomeProject'
      EXTRA_ARGS: '--only functions'
      DEBUG: 'true'
```

If you have multiple targets to deploy, you have to specify appropriate targets in firebase.json and then use the pipe in following ways:

- Deploying multiple sites at once

```yaml
script:
  - pipe: atlassian/firebase-deploy:2.0.0
    variables:
      FIREBASE_TOKEN: $FIREBASE_TOKEN
      PROJECT_ID: 'myAwesomeProject'
      MESSAGE: 'Deploying myAwesomeProject'
      EXTRA_ARGS: '--only functions'
      MULTI_SITES_CONFIG: >
          [{
            "TARGET": "my-application-target",
            "RESOURCE": "my-appropriate-resource"
          },
          {
            "TARGET": "my-app-blog-target",
            "RESOURCE": "resource1.blog.com resource2.blog.com"
          }]
      DEBUG: 'true'
```

- Deploying multiple sites at parallel steps:

```yaml
- parallel:
  - step:
    script:
      - pipe: atlassian/firebase-deploy:2.0.0
        variables:
          FIREBASE_TOKEN: $FIREBASE_TOKEN
          PROJECT_ID: 'myAwesomeProject'
          MESSAGE: 'Deploying myAwesomeProject'
          EXTRA_ARGS: '--only functions'
          MULTI_SITES_CONFIG: >
              [{
                "TARGET": "my-application-target1",
                "RESOURCE": "my-appropriate-resource"
              }]
          DEBUG: 'true'
  - step:
    script:
      - pipe: atlassian/firebase-deploy:2.0.0
        variables:
          FIREBASE_TOKEN: $FIREBASE_TOKEN
          PROJECT_ID: 'myAwesomeProject'
          MESSAGE: 'Deploying myAwesomeProject'
          EXTRA_ARGS: '--only functions'
          MULTI_SITES_CONFIG: >
              [{
                "TARGET": "my-app-blog-target",
                "RESOURCE": "resource1.blog.com resource2.blog.com"
              }]
          DEBUG: 'true'
```

- Deploying just one specific site.
 
For easier use we recommend to deploy one site at a step to have better deploy workflow.

For more information about multiple targets see [Firebase Deploy Targets][Firebase Deploy Targets].

## Support
If you’d like help with this pipe, or you have an issue or feature request, [let us know on Community][community].

If you’re reporting an issue, please include:

- the version of the pipe
- relevant logs and error messages
- steps to reproduce


## License
Copyright (c) 2018 Atlassian and others.
Apache 2.0 licensed, see [LICENSE.txt](LICENSE.txt) file.


[community]: https://community.atlassian.com/t5/forums/postpage/board-id/bitbucket-questions?add-tags=bitbucket-pipelines,pipes,google,deployment,firebase
[Google service account]: https://cloud.google.com/iam/docs/creating-managing-service-account-keys
[encode private key docs]: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/#Use-multiple-SSH-keys-in-your-pipeline
[firebase doc]: https://firebase.google.com/docs/cli/targets#configure_firebasejson_to_use_deploy_targets
[Installing the Firebase CLI]: https://firebase.google.com/docs/cli/#install_the_firebase_cli
[command reference]: https://firebase.google.com/docs/cli/#administrative_commands
[Firebase Deploy Targets]: https://firebase.google.com/docs/cli/targets
[NodeJS]: https://nodejs.org/en/about/releases/
[Firebase runtime]: https://firebase.google.com/docs/functions/manage-functions#set_runtime_options
