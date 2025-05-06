#!/bin/bash

echo "🔐 Allowing the root user (as used in the Docker container) to access the X display server (for GUI support)..."
xhost +local:root

echo "🐳 Starting the ORB-SLAM3 Docker container..."
docker-compose run orbslam3-spell

echo "🔒 Revoking X server access from Docker (cleanup)..."
xhost -local:root

echo "✅ Done! ORB-SLAM3 container has exited and X access has been restored."