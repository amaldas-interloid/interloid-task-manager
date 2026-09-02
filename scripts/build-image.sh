#!/bin/bash

set -e

IMAGE_NAME="interloid-task-manager"
TAG="latest"

echo "Building Docker image..."

docker build -t "${IMAGE_NAME}:${TAG}" .

echo "Docker image built successfully."