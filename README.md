# ORBSLAM3_implementation
My own attempt at implementing ORBSLAM3

Original repo: https://github.com/UZ-SLAMLab/ORB_SLAM3 
Last updated: Dec 2021

I'm going to follow the implementation by kevin-robb: https://github.com/kevin-robb/orb_slam_implementation

## Phase 1: Environment Setup

### System preparation

>[!NOTE]
> The following WSL installation was only used during development. 

- [x] Install a fresh Ubuntu 20.04 on a virtual machine

>[!TIP]
> Make sure you allocate at least 16GB of RAM and 4 CPU cores to the virtual machine. 32GB of RAM is recommended.

I'm going to run Ubuntu on [Windows Subsytem for Linux (WSL)](https://documentation.ubuntu.com/wsl/en/latest/) instead than on a virtual machine like VMware Workstation. 

WSL enables us to run a GNU/Linux environment on Windows. Once installed, Ubuntu can be used as a terminal interface on Windows and can launch any linux-native applications.

IF you don't have the latest WSL install you can run in the command line as administrator the following
```
> wsl --install
``` 

To install Ubuntu 20.04 runn
```
> wsl --install -d Ubuntu-20.04
``` 

You can check all the different distributions install on your Windows machines by typing `> wsl -l -v`

To open Ubuntu, run `> ubuntu2004.exe` in the command line. 

Make sure to install all the latest updates by runnign the following commands

```
$ sudo apt update
$ sudo apt full-upgrade -y
```

To access your local documents in your Windows PC from an Ubuntu terminal using WSL, you can run the following command from an Ubuntu terminal:

```
cd /mnt/c/Users/<your_Windows_username>
ls
```
>[!IMPORTANT]
> It's important to understand that the home directory in Ubuntu/WSL is not the same as your Windows home directory, nor should it be. Your Ubuntu home directory is in a virtual SSD provided by WSL. This virtual SSD provides the Linux compatible filesystem that Ubuntu needs, whereas your Windows drive is formatted as NTFS and won't have 100% compatibility.

- [ ] Install dependencies -- not sure if I will end needing to do this.

Install the following necessary packages:

- Build tools: `build-essential`, `cmake`, and `git`.
- Libraries: `libgtk2.0-dev`, `pkg-config`, `libavcodec-dev`, `libavformat-dev`, `libswscale-dev`, `python-dev`, `python-numpy`, `libtbb2`, `libtbb-dev`, `libjpeg-dev`, `libpng-dev`, `libtiff-dev`, `libdc1394-22-dev`, `libjasper-dev`, `libglew-dev`, `libboost-all-dev`, `libssl-dev`, `libeigen3-dev`, and `libcanberra-gtk-module`.

I'm going to deviate from Kevin Robbs's setup and attempt to build everything with docker instead. 

### Setup docker

Instad of following Kevin Robb's setup, I'm going to build a docker around the ORBSLAM3 implementation.This docker should

- [ ] Start from an Ubuntu 20.04 image
- [ ] Install all `apt` dependencies
- [ ] Install OpenCV 4.2 and 3.2 from source
- [ ] Build Pangolin 
- [ ] Build ORBSLAM3 with patches
- [ ] Install python dependencies in the image
- [ ] Mount my datasets/configs via volumes
- [ ] Optional: include ROS support 

After this I need
- [ ] build the docker image 
- [ ] run the container
- [x] (optional) add a `docker-compose.yml` file to run it including local datasets, any custom config files...
- [x] (optional) a launch script `run_docker.sh` --> how would this work? how is it different from docker-compose?
- [ ] (optional) how to include GPU support (CUDA)

#### Write the dockerfile backbone

Dockerfile can be found [here](docker/Dockerfile).

Created a [docker-compose](docker/docker-compose.yml) file. With this file I can avoid having to type long `docker run` like those needed to mount volumes (e.g., `docker run -i container-name -v ~/ORBSLAM3_implementation/src:/app`). This file describes the services, volumes, networks, enviornment, and how to build and run everything in my environment.

In this YAML file I can define:
- how to build the Dockerfile into an image
- how to run the container
- what volumes to mount
- what environment variable sto use
- more (networks, multiple services, ports...)

Instead of writing long `docker build` and `docker run` commands, I can just run:
```
cd docker
docker-compose build #builds the docker image(s) defined in the compose file
docker-compose run orbslam3-spell #runs a one-time interactive instance of the container; last argument is the service (container) name

#optional
docker-compose up #starts all the services/containers in the background (e.g, ROS2 + GPU + SLAM pipeline)
```
#### Wrap all dependencies
##### Build Pangolin
Pangolin is a lightweight C++ library for visualization and GUI. You can use it to display 3D camera trajectories, render the map, show keyframes and landmarks, and provie a real-time GUI window to interact with the SLAM pipeline. 

Pangolin is a hard dependency. The visual side of ORB-SLAM3 won't work without it. 

Pangolin is cloned inside the [Dockerfile](docker/Dockerfile).

##### Install OpenCV
Based on Kevin Robb's implementation instructions, we need to:
1. Clone OpenCV twice: versions 4.2.0 and 3.2.0
2. Make a small manual patch to both versions of a source file
3. Build and install each version separately
4. Rename one to avoid conflict



---
docker commands (to be removed later on):
```
docker image sl  #list all images, also docker images
docker image pull # pull image from docker hub e.g., docker image pull ros:humble; it also works with docker pull
docker image rm name-image #remove image; if a container is already built you can force delete by adding -f after rm; also works with docker rmi name-image

docker image build -t image-name . #from image to container, also works with docker build; note '.' for current directory 

docker container ls #list containers; also works with docker ps 

docker run image-name #run the container
docker run -it image-name #to request a terminal inside the container not just run it

docker container stop container-name # stop a container; docker will give containers random names but you can also give it a name of your choosing with --name <container-name> <image-name>

docker run -i container-name # (re)start a container

docker container rm container-name #remove container; also works with docker rm
docker contianer prune #delete all containers

docker exec -it container-name /bun/bash #open a new terminal within a container (to open more than one terminal)
docker exec -it container-name ls #run other commands inside a container, in this case 'ls'

# how to access and work on files outside the container
# assume we have a local directory called source/something.py
docker run -it -v $PWD/source:/my_source_code image-name # my_source_code is how the directory source will be named inside the docker image (the copy of the folder will be renamed as my_source_code)

```
