# ORBSLAM3_implementation
My own attempt at implementing ORBSLAM3

Original repo: https://github.com/UZ-SLAMLab/ORB_SLAM3 
Last updated: Dec 2021

I'm going to follow the implementation by kevin-robb: https://github.com/kevin-robb/orb_slam_implementation

## Phase 1: Environment Setup

### System preparation

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

- [] Install dependencies

Install the following necessary packages:

- Build tools: `build-essential`, `cmake`, and `git`.
- Libraries: `libgtk2.0-dev`, `pkg-config`, `libavcodec-dev`, `libavformat-dev`, `libswscale-dev`, `python-dev`, `python-numpy`, `libtbb2`, `libtbb-dev`, `libjpeg-dev`, `libpng-dev`, `libtiff-dev`, `libdc1394-22-dev`, `libjasper-dev`, `libglew-dev`, `libboost-all-dev`, `libssl-dev`, `libeigen3-dev`, and `libcanberra-gtk-module`.

I'm going to deviate from Kevin Robbs's setup and attempt to build everything with docker instead. 

### Setup docker

I need to do the following
1. Writing a base Dockerfile for Ubuntu 20.04
2. Adding all system dependencies
3. Building OpenCV from source
4. Installing Pangolin+Eigen 
5. Cloning and building ORB-SLAM3

#### Write a dockerfile

A dockerfile is a blueprint for building a complete ORB-SLAM3 environment.

DONE

next steps:
- building the docker image `docker build -t orbslam3`
- run the container `docker run -it --rm orbslam3`

optional next steps I don't fully understand yet:
- add a `docker-compose.yml` file to run it including local datasets, any custom config files...
- a launch script `run_docker.sh` --> how would this work? how is it different from docker-compose?
- mounting specific datasets and configs
- building and running the docker
