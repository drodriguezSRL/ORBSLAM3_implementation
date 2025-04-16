#!/bin/bash

echo "🔐 Allowing Docker container to access the X server (for GUI support)..."
xhost +local:root

echo "🐳 Starting the ORB-SLAM3 Docker container..."
docker-compose run --rm orbslam3-spell

echo "🔒 Revoking X server access from Docker (cleanup)..."
xhost -local:root

echo "✅ Done! ORB-SLAM3 container has exited and X access has been restored."