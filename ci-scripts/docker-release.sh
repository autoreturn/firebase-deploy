#!/usr/bin/env bash
#
# Release to dockerhub.
#
# Required globals:
#   DOCKERHUB_USERNAME
#   DOCKERHUB_PASSWORD

set -ex

IMAGE=$1
VERSION=2.0.0-2

echo ${DOCKERHUB_PASSWORD} | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
docker build -t ${IMAGE} .
docker tag ${IMAGE}:${VERSION}
docker push ${IMAGE}:${VERSION}
