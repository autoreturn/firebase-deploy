#!/bin/bash

IMAGE=$1

docker run -it --env PROJECT_ID="project-id" --env FIREBASE_TOKEN="token" --env FIREBASE_COMMAND="--version" ${IMAGE}
