# How was ORBSLAM3_implementation done

This describes how this ORBSLAM3 docker implementation was done. It includes all the bugs and workarounds that were needed to make it work.
The goal of this file is to leave a record of everything that's behind what's included in this repository. 
I used this file as a log book of every step I took (and planned on taking, thus the present tense used at times) during development. 


Since this was one of the first times for me working intensively with Docker, I created my own cheatlist of Docker commands, which can be found [here](#docker-commands). 

## Phase 1: Environment setup

### Install a fresh Ubuntu 20.04

I'm going to run Ubuntu on [Windows Subsytem for Linux (WSL)](https://documentation.ubuntu.com/wsl/en/latest/) instead than on a virtual machine like VMware Workstation. 

WSL enables us to run a GNU/Linux environment on Windows. Once installed, Ubuntu can be used as a terminal interface on Windows and can launch any linux-native applications.

IF you don't have the latest WSL install you can run in the command line as administrator the following:

```
> wsl --install
``` 

To install Ubuntu 20.04 run:

```
> wsl --install -d Ubuntu-20.04
``` 

You can check all the different distributions install on your Windows machines by typing `> wsl -l -v`

To open Ubuntu, run in the command line:
 
```
ubuntu2004.exe 
```

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

>[!TIP]
> In case of using a virtual machine instead, make sure you allocate at least 16GB of RAM and 4 CPU cores to the virtual machine. 32GB of RAM is recommended.

--- 
**NOTE ON HYPER-V**

In the event that your Windows system has hypervisor disabled (e.g., if you need to run programs such as TwinCAT incompatible with virtualization enviornments), you can turn it back on by opening a PowerShell in admin mode and running the following command:

```
bcdedit /set hypervisorlaunchtype auto
```

The change will take effect after restarting your computer. 

Important Considerations:
- Virtualization-based Security (VBS): Disabling Hyper-V can also disable VBS, which can impact security features. 
- Reverting the change: To switch Hyper-V off again, use `bcdedit /set hypervisorlaunchtype off` in the command line and reboot. 
- Other methods: You can also disable Hyper-V through the "Turn Windows features on or off" settings, says [Learn Microsoft](https://learn.microsoft.com/en-us/troubleshoot/windows-client/application-management/virtualization-apps-not-work-with-hyper-v).  
---

### Setup docker 

Here is were I deviated from Kevin Robb's implementation. I ended up wrapping everything inside a Dockerfile.

The following is included in the [Dockerfile](docker/Dockerfile).

- [x] Start from an Ubuntu 20.04 image
- [x] Install all `apt` dependencies
- [x] Install OpenCV 4.2 and 3.2 from source
- [x] Build Pangolin 
- [x] Build ORBSLAM3 with patches
- [x] Install python dependencies in the image
- [x] Mount my datasets/configs via volumes
- [ ] Optional: include ROS support 

I created a [docker-compose](docker/docker-compose.yml) file. With this file I can avoid having to type long `docker run` commands like those needed to mount volumes (e.g., `docker run -i container-name -v ~/ORBSLAM3_implementation/src:/app`). This file describes the services, volumes, networks, environment variables, and how to build and run everything in my environment.

In this YAML file I can define:
- how to build the Dockerfile into an image
- how to run the container
- what volumes to mount
- what environment variables to use
- more (networks, multiple services, ports...)

With this `docker-compose.yml`file, instead of writing long `docker build` and `docker run` commands, I can just build the Docker image with:

```
cd docker
docker-compose build
```

And run the image into a container with (note that `orbslam3-spell` is the name I gave to the service inside the `docker-compose.yml` file):

```
docker-compose run orbslam3-spell 
```

>[!NOTE]
> Volumes are mounted when the container is run, not when the image is built. If you change volumes within the docker-compose file, simply re-running the container will apply those changes. We only need to rebuild images if changes are made to the `Dockerfile` itself.

Optionally we can start all services/containers in the background (e.g., ROS2 + GPU + SLAM pipeline) with:

```
docker-compose up 
```

### Building the Dockerfile backbone

#### Install system dependencies

Include the following necessary packages into the Dockerfile:

- Build tools: `build-essential`, `cmake`, and `git`.
- Libraries: `libgtk2.0-dev`, `pkg-config`, `libavcodec-dev`, `libavformat-dev`, `libswscale-dev`, `python-dev`, `python-numpy`, `libtbb2`, `libtbb-dev`, `libjpeg-dev`, `libpng-dev`, `libtiff-dev`, `libdc1394-22-dev`, `libjasper-dev`, `libglew-dev`, `libboost-all-dev`, `libssl-dev`, `libeigen3-dev`, and `libcanberra-gtk-module`.

#### Build Pangolin
Pangolin is a lightweight C++ library for visualization and GUI. You can use it to display 3D camera trajectories, render the map, show keyframes and landmarks, and provie a real-time GUI window to interact with the SLAM pipeline. 

Pangolin is a hard dependency. The visual side of ORB-SLAM3 won't work without it. 

Pangolin is cloned inside the [Dockerfile](docker/Dockerfile).

#### Install OpenCV
Based on Kevin Robb's implementation instructions, we need to:
1. Clone OpenCV twice: versions 4.2.0 and 3.2.0
2. Make a small manual patch to both versions of a source file
3. Build and install each version separately
4. Rename one to avoid conflict

The last step is not needed if we clone and build both versions in separate folders `opencv4`and `opencv3` from the start.

>[!CAUTION]
> The two OpenCV installs will conflict if you try to use both at the same time. So you should:
> - Either link only the one you need in your CMake project
> - or set up CMake options to use specific OpenCV versions via `OpenCV_DIR`

>[!TIP]
> If you want help switching between the two versions within ORB-SLAM3 builds, I can show you how to do that in the `CMakeLists.txt` using `OpenCV_DIR` environment variables.

#### Install ORB-SLAM3
Based on Kevin Robb's implementation instructions, I need to:
1. Clone the repo
2. Checkout the exact commit
3. Path the files (LoopClosing.h, System.cc, CMakeList.txt)
4. Run the `build.sh` script
5. Handle possible build hiccups (retry if needed)

>[!WARNING]
> I haven't been able (yet) to build ORB-SLAM3 into the Docker image. I manage to get it to work by building ORB-SLAM3 by hand within the container. 

## Phase 2: Automate dataset download

I'm going to write a bash script to download the `EuRoC MH_01_easy`dataset, unzip it, and detect and fix all corrupted images.

- [x] Create the download_euroc_mh01.sh file

### Download Example Data: EuRoC MH_01 easy

Run the following command:

```
./download_euroc_mh01.sh
```

>[!IMPORTANT]
> Running the dataset setup script should be done before building and running the docker. The dataset directory should be mounted into the docker container. 


## Phase 3: Testing and debugging 

This section lists all the warning and errors I got in the process of developing this ORB-SLAM3 implementation. It also includes all the associated actions I took to troubleshoot and fix the errors. 

**WARNINGS:**
- [W1] `WARN[0000] /home/rodriguez/ORBSLAM3_implementation/docker/docker-compose.yml: the attribute "version" is obsolete, it will be ignored, please remove it to avoid potential confusion`

**ERRORS:** 
- [E1] Build requires input about geography zone
- [E2] RUN git clone https://github.com/stevenlovegrove/Pangolin.git && ...cmake .. *_DCMAKE_BUILD_TYPE=Release* && make -j$(nproc) && make install
- [E3] OpenCV 3.2.0 and python compiler version mismatch 
- [E4] WSL appears to crash when running build.sh for ORBSLAM. This could be due to memory or CPU limits being exceeded (long build + heavy script)
- [E5] `what(): Pangolin X11: Failed to open X display`: ORB-SLAM3 application (which uses Pangolin for visualization) is trying to open a graphical window, but can’t access the host's X display (your graphical environment). . 

**ACTIONS:**
- [W1] Remove version for `docker-compose.yml`
- [E1] Add `DEBIAN_FRONTEND=noninteractive` to `Dockerfile` 
- [E2] Fix typo in `Dockerfile`, from `_DCMAKE_BUILD_TYPE=Release` to `-D CMAKE_BUILD_TYPE=Release`
- [E3] Before changing anything major, I checked the libraries installed and some didn't match Kevin's implementation. Changed `Dockerfile` to match Kevin's to the letter. Fixed.
- [E4] Checkiong current WSL limits. Extended WSL memory in `.wslconfig` to 8GB. Stil crushing. Could be due to building from VSCode? Trying to build container without running ORBSLAM3 `build.sh`. Success. Trying to run container in PowerShell and build ORBSLAM3 from whithin by running `sh build.sh` inside the `ORBSLAM-3`folder. Lots of errors and warnings. Run it 3 times. Built ORBSLAM3 succesfully after 3 attempts. No changes made. Name of the container `great_jackson`. 
- [E5] Pangolin relies on X11, the Linux windowing system. Inside Docker, there's no GUI access by default, unless we give it permission. 

First, we need to give permision to the `root` user to access X display by running `xhost +local:root` in the terminal where the Docker container will be run. We could also give permision to all local users with `xhost +local:` or even to all users with `xhost +`. Permissions can be revoked by the same commands simply swapping `+`for `-`. I'm going to create a basch script to simplify this workflow by running this command followed by running the container. 

We also need to expose the X domain socket. When running the container, we want to create a new volume that maps `/tmp/.X11-unix` to `:/tmp/.X11-unix:rw`. I included this within the `docker-compose.yml` volumes.

The third thing we need is giving it at X display by setting up the X environment variable. We can tell docker to use the same one the host is using `--env=DISPLAY`. I included this argument within my `docker-compose.yml` environment as `DISPLAY=${DISPLAY}`. 

>[!TIP]
> We can also run the container as a user that has permision to access X display, e.g., run the container as a user that matches the host. 

**Success**: name of the current container `docker-orbslam3-spell-run-ee6c1ca75dba`.


## Phase 4: What's next...

Things I still need to do:

- [x] build the docker image 
- [x] run the container
- [x] debug with euroc mh01 dataset
- [ ] how to build ORBSLAM3 from within the Dockerfile
- [ ] learn about adding sudo to docker
- [ ] learn about adapting my own data to work with ORBSLAM3
- [x] (optional) add a `docker-compose.yml` file to run it including local datasets, any custom config files...
- [x] (optional) a launch script `run_docker.sh` --> how would this work? how is it different from docker-compose? --> written but haven't used it yet. not sure I need the permissions line.
- [ ] (optional) what is `entrypoint.sh` for? how could I use it?
- [ ] (optional) how to include GPU support (CUDA)
- [ ] try it out on windows terminal
- [ ] adapt to other common datasets
- [ ] adapt to spice hl3


## Docker commands [#docker-commands]

```
docker image sl  #list all images, also docker images
docker image pull # pull image from docker hub e.g., docker image pull ros:humble; it also works with docker pull
docker image rm name-image #remove image; if a container is already built you can force delete by adding -f after rm; also works with docker rmi name-image

docker image build -t image-name . #from image to container, also works with docker build; note '.' for current directory 

docker container ls #list active/running containers; also works with docker ps 
docker  ps -a # list all containers even if stopped

docker run image-name #run the container
docker run -it image-name #to request a terminal inside the container not just run it

docker container stop container-name # stop a container; docker will give containers random names but you can also give it a name of your choosing with --name <container-name> <image-name>
docker container start -i container-name #re-start a container

docker run -i container-name # (re)start a container

docker container rm container-name #remove container; also works with docker rm
docker container prune #delete all containers

docker exec -it container-name /bun/bash #open a new terminal within a container (to open more than one terminal)
docker exec -it container-name ls #run other commands inside a container, in this case 'ls'

# how to access and work on files outside the container
# assume we have a local directory called source/something.py
docker run -it -v $PWD/source:/my_source_code image-name # my_source_code is how the directory source will be named inside the docker image (the copy of the folder will be renamed as my_source_code)

```