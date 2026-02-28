# How was ORBSLAM3_implementation done

This doc describes how this ORBSLAM3 docker implementation was done. It includes all the steps, bugs, and workarounds that I needed to take to make it work.

I originally used this file as a personal log book, documenting for my own sake every step I took during development. 

It wasn't intended to be publicly released but decided otherwise once the implementation was finally working. 

Take everything said in here with a great deal of skepticism as I'm no expert sw developer. I'm sure there are different, and definitely better, ways of going about some of the steps I took. But this is what worked for me, and it may work for you too. 

- [How was ORBSLAM3\_implementation done](#how-was-orbslam3_implementation-done)
  - [Phase 1: Environment setup](#phase-1-environment-setup)
    - [Install a fresh Ubuntu 20.04](#install-a-fresh-ubuntu-2004)
    - [Setup docker](#setup-docker)
    - [Building the Dockerfile backbone](#building-the-dockerfile-backbone)
      - [Install system dependencies](#install-system-dependencies)
      - [Build Pangolin](#build-pangolin)
      - [Install OpenCV](#install-opencv)
      - [Install ORB-SLAM3](#install-orb-slam3)
      - [Adding a non-root user](#adding-a-non-root-user)
      - [Enabling sudo](#enabling-sudo)
  - [Phase 2: Automating dataset download](#phase-2-automating-dataset-download)
    - [Download Example Data: EuRoC MH\_01 easy](#download-example-data-euroc-mh_01-easy)
  - [Phase 3: Testing and debugging](#phase-3-testing-and-debugging)
  - [Phase 4: Output and results analysis](#phase-4-output-and-results-analysis)
  - [Phase 5: Adapting my own data](#phase-5-adapting-my-own-data)
    - [Adapting the directory layout](#adapting-the-directory-layout)
    - [Adapting the data itself](#adapting-the-data-itself)
    - [Testing new data](#testing-new-data)
  - [Docker commands](#docker-commands)
  - [Things to improve](#things-to-improve)


>[!NOTE]
> Since this was one of the first times for me working intensively with Docker, I created my own cheatlist of Docker commands, which, in case you are a newbie like me, can be found [here](#docker-commands). 

## Phase 1: Environment setup

### Install a fresh Ubuntu 20.04

I ran Ubuntu on [Windows Subsytem for Linux (WSL)](https://documentation.ubuntu.com/wsl/en/latest/) instead than on a virtual machine like VMware Workstation. 

WSL enables us to run a GNU/Linux environment on Windows. Once installed, Ubuntu can be used as a terminal interface on Windows and can launch any linux-native applications.

If you don't have the latest WSL install you can run the following in the command line as administrator:

```
wsl --install
``` 

To install Ubuntu 20.04 run:

```
wsl --install -d Ubuntu-20.04
``` 

You can check all the different distributions install on your Windows machine by typing `> wsl -l -v`. You can also check a list of all distributions available online for installation by running `wsl -l --online`. 

To open Ubuntu, run in the command line:
 
```
ubuntu2004.exe 
```

Make sure to install all the latest updates by running the following commands

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

In the event that your Windows system has hypervisor disabled (e.g., if you need to run sw tools such as TwinCAT incompatible with virtualization environments), you can turn it back on by opening a PowerShell in admin mode and running the following command:

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

Here is where I deviated from Kevin Robb's implementation. I ended up wrapping everything inside a Dockerfile.

The following is included in the [Dockerfile](docker/Dockerfile).

- [x] Start from an Ubuntu 20.04 image
- [x] Install all `apt` dependencies
- [x] Install OpenCV 4.2 and 3.2 from source
- [x] Build Pangolin 
- [x] Build ORBSLAM3 with patches
- [x] Install python dependencies in the image
- [x] Mount my datasets/configs via volumes
- [ ] Optional: include ROS support 

I created a [docker-compose](docker/docker-compose.yml) file. With this file I avoided having to type long `docker run` commands like those needed to mount volumes (e.g., `docker run -i container-name -v ~/ORBSLAM3_implementation/src:/app`). This file describes the services, volumes, networks, environment variables, and how to build and run everything in my environment.

In this YAML file I can define:
- how to build the Dockerfile into an image
- how to run the container
- what volumes to mount
- what environment variables to use
- more (networks, multiple services, ports...)

With this `docker-compose.yml` file, instead of writing long `docker build` and `docker run` commands, I can just build the Docker image with:

```
cd docker
docker-compose build
```

And run the image into a container with (note that `orbslam3-spell` is the name I gave to the service inside the `docker-compose.yml` file):

```
docker-compose run orbslam3-spell 
```

>[!NOTE]
> Volumes are mounted when the container is run, not when the image is built. If you change volumes within the docker-compose file, simply re-running ("rebuilding") the container will apply those changes. We only need to rebuild images if changes are made to the `Dockerfile` itself.

Optionally we can (re)build the image and start the container all at once with `docker-compose up`. To do this in the background (aka 'detached mode') (e.g., ROS2 + GPU + SLAM pipeline) we can use:

```
docker-compose up -d
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

#### Install ORB-SLAM3

Based on Kevin Robb's implementation instructions, I need to:
1. Clone the repo
2. Checkout the exact commit
3. Path the files (LoopClosing.h, System.cc, CMakeList.txt)
4. Run the `build.sh` script
5. Handle possible build hiccups (retry if needed)

>[!WARNING]
> I haven't been able (yet) to build ORB-SLAM3 into the Docker image. I managed to get it to work by manually building ORB-SLAM3 within the container. 

#### Adding a non-root user

>[!NOTE]
> No non-root user has been included in the latest version of the docker image.

By default we operate inside the container with the `root` user (UID=0, GID=0). 

If we wanted to create a new user, say `orbuser`, the following will need to be included in the [Dockerfile](/docker/Dockerfile):

```
ARG USERNAME=orbuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# create a non-root user
RUN groupadd --gid $USER_GID $USERNAME && \ 
    useradd -s /bin/bash --uid $USER_UID --gid $SUER_GID -m $USERNAME && \
    mkdir /home/$USERNAME/.config && chown $USER_UID:$USER_GID /home/$USERNAME/.config


RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    chown -R $USERNAME:$USERNAME /app
```

In case we need to use the new user inside the docker file (to create new files with specific user permissions for istance), this can be done by adding the following to the [Dockerfile](/docker/Dockerfile):

```
# Switch to non-root user
USER $USERNAME

```

Any other instructions that take place after that line will be issued as that user. To return to `root`(to install something, for instance), all you need to do is retype `USER root`.

> [!TIP]
> It is actually a good practice, if you are using non-root users in your Dockerfile, to end your Dockerfile by swapping back to the root user. This way, anyone else building off your image will do so from root. 

Then in the [docker-compose](/docker/docker-compose.yml) file, include:

```
services:
    orbslam3-spell:
        ...
        user: "1000:1000" # matches USER_UID:USER_GID in Dockerfile
        ...
```

#### Enabling sudo 

Add the following to the [Dockerfile](/docker/Dockerfile) to enable `sudo` and grant root permissions to a specific user: 

```
# set up sudo
RUN apt-get udpate && \
    apt-get install -y sudo && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    rm -rf /var/lib/apt/lists/*
```

## Phase 2: Automating dataset download

I wrote a bash script to download the `EuRoC MH_01_easy`dataset, unzip it, and detect and fix all corrupted images.

- [x] Create the [download_euroc_mh01.sh](./download_euroc_mh01.sh) file

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

First, I needed to give permision to the `root` user to access X display by running `xhost +local:root` in the terminal where the Docker container will be run. I could also give permision to all local users with `xhost +local:` or even to all users with `xhost +`. Permissions can be revoked by the same commands simply swapping `+`for `-`. I could create a basch script to simplify this workflow by running this command followed by running the container. 

I also needed to expose the X domain socket. When running the container, I want to create a new volume that maps `/tmp/.X11-unix` to `:/tmp/.X11-unix:rw`. I included this within the `docker-compose.yml` volumes.

The third thing we need is giving it an X display by setting up the X environment variable. I can tell docker to use the same one the host is using `--env=DISPLAY`. I included this argument within my `docker-compose.yml` environment as `DISPLAY=${DISPLAY}`. 

>[!TIP]
> You can also run the container as a user that has permision to access X display, e.g., run the container as a user that matches the host. 

**:fire Success :fire**

## Phase 4: Output and results analysis

ORB-SLAM3 generates two output files for each trajectory (+info in [orbslam3_explained](/orbslam3_explained.md)):
- `f_dataset-MH01_stereo.txt`
- `kf_dataset-MH01_stereo.txt`

So far, files are saved under the main `ORB_SLAM3` directory. I don't think output files should be processed inside the container. Best would be for these files to be accessible from host and the postprocessing and evaluation to take place in host, instead. To make files accessible from host I have two options

**A. Mount a new volume accessible from the outside and force ORB-SLAM's output to be saved there**

For this, I could create a new volume `output` in the `docker-compose` file so that files are saved there after running ORB-SLAM3. 

I will need to hardcode a different path in the source code so that ORB-SLAM3 saves the output in the right directory. In particular, I need to change where files are saved toward the end of the `main()` function in the demo executable (i.e., `stereo_euroc.cc` for instance). Replacing 

```
SLAM.SaveTrajectoryEuRoC(f_file);
SLAM.SaveKeyFrameTrajectoryEuRoC(kf_file);
```

with

```
SLAM.SaveTrajectoryEuRoC(/your/output/path/f_file);
SLAM.SaveKeyFrameTrajectoryEuRoC(/your/output/path/kf_file);
```
Main problem with this is that the exectuable needs to be recompiled. 

**B. Manually copy the files from the container to a directory in the host**

Since option A would require re-running the container (starting fresh), I could instead use `docker cp` to copy files from container to host. Running a command like:

```
docker cp <container_id>:/path/in/container/file.txt /host/destination/
```

Independently from which of these two options I choose (A or B), ORB-SLAM3 provides a script to evaluate the generated trajectory against the ground truth. This script can be found in `~/Dev/ORB_SLAM3/evaluation/evaluate_ate_scale.py` and also in [/tools](/tools/) within this repository.

>[!IMPORTANT]
> From [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3): it should be noted that EuRoC provides ground truth for each sequence in the IMU body reference. As pure visual executions report trajectories centered in the left camera, the script `evaluate_ate_scale.py` provides in the "evaluation" folder the transformation of the ground truth to the left camera reference. Visual-inertial trajectories use the ground truth from the dataset.

## Phase 5: Adapting my own data

I adapted the [SPICE-HL3 dataset](https://github.com/spaceuma/spice-hl3) to work with ORB-SLAM3.

I first attempted to adapt and run ORB-SLAM3 over SPICE-HL3 **Trajectory F** stereo-inertial data. 

The best strategy IMO was to try to emulate the layout and setup of the working example whose sensor configuration matches that of the new dataset. In this case that would be the Stereo+IMU configuration. 

Make sure you understand the parsing of arguments when running the `stereo_inertial_euroc` example. More info [here](/orbslam3_explained.md). As a summary, we have:

1. Executable wrapper: `stereo_inertial_euroc.cc` 
2. Vocabulary: `ORBvoc.txt`
3. Configuration: `EuRoc.yaml`
4. Path to dataset: `~/Datasets/EuRoc/MH01`
5. Timestamps: `MH01.txt`
6. Output file name: `dataset-MH01_stereoi`

>[!IMPORTANT]
> The fastest strategy for making your own dataset work with ORB-SLAM3 is to rely on the already existing and compiled executables like `stereo_inertial_euroc`. It's recommended to use these same executable files when running ORB-SLAM3 since they are already compiled when ORB-SLAM3 is built. Therefore, you only need to adapt the directory structure to match the one expected by the executable to be used.  

### Adapting the directory layout

I adapted the `spice-hl3` directory structure to work with the `./Examples/Stereo-Inertial/stereo_inertial_euroc` launch file. 

First thing I did is to create a new directory, which I created in the ' /data' folder that is later on mounted to `~/Datasets`, which micmicks what's inside the docker at `~/Dev/ORB_SLAM3/Examples/`. This new directory is called `spice-hl3`. 

In this directory I included the following:

```bash
spice-hl3
    ├── trajectoryA
    │   └──mav0
    │       ├── cam0
    │       │   ├── data
    │       │   │   ├── _timestamp_.png
    │       │   │   ├── ...
    │       │   │   └── ...
    │       │   ├── data.csv
    │       │   └── sensor.yaml
    │       ├── cam1
    │       │   ├── data
    │       │   ├── data.csv
    │       │   └── sensor.yaml
    │       └── imu0
    │           ├── data.csv
    │           └── sensor.yaml
    ├── trajectoryB
    │   └──mav0
    │       ├── ...
    ├── ...
    ├── config
    │   ├── spice-hl3_mono.yaml
    │   ├── spice-hl3_mono-inertial.yaml
    │   ├── spice-hl3_stereo.yaml
    │   └── spice-hl3_stereo-inertial.yaml
    └── timestamps 
        ├── trajectoryA.txt
        ├── trajectoryB.txt
        ├── ...
        └── trajectoryG.txt
```

With this directory layout and the data structure defined below, I could run any of the following commands from inside the container (note the use of the same euroc executable and the same ORB-SLAM3 vocabulary):

```
# Mono
./Examples/Monocular/mono_euroc ./Vocabulary/ORBvoc.txt ~/Datasets/spice-hl3/config/spice-hl3_mono.yaml ~/Datasets/spice-hl3/trajectoryF ~/Datasets/spice-hl3/timestamps/trajectory_F.txt dataset-spicehl3_trjF_mono

# Mono + Inertial
./Examples/Monocular-Inertial/mono_inertial_euroc ./Vocabulary/ORBvoc.txt ~/Datasets/spice-hl3/config/spice-hl3_mono-inertial.yaml ~/Datasets/spice-hl3/trajectoryF ~/Datasets/spice-hl3/timestamps/trajectory_F.txt dataset-spicehl3_trjF_monoi

# Stereo
./Examples/Stereo/stereo_euroc ./Vocabulary/ORBvoc.txt ~/Datasets/spice-hl3/config/spice-hl3_stereo.yaml ~/Datasets/spice-hl3/trajectoryF ~/Datasets/spice-hl3/timestamps/trajectory_F.txt dataset-spicehl3_trjF_stereo

# Stereo + Inertial
./Examples/Stereo-Intertial/stereo_interial_euroc ./Vocabulary/ORBvoc.txt ~/Datasets/spice-hl3/spice-hl3.yaml ~/Datasets/spice-hl3/trajectoryF ~/Datasets/spice-hl3/timestamps/trajectory_F.txt dataset-spicehl3_trjF_stereoi
```

>[!IMPORTANT]
> The timestamps for both `cam0` (_left stereo camera_) and `cam1` (_right stereo camera_), including the `MH01.txt`(which is created from the timestamps of `cam0`), must be the same exact timestamps. This is key because ORB-SLAM3 will look for left and right camera images matching the timestamps listed in the `*.txt` timestamps file. 

### Adapting the data itself 

This section contains a few of the things that I had to do to make SPICE-HL3 work with ORB-SLAM3. This information is only included as a reference. The steps you need to take to adapt your own data are pretty much dependent on your data itself. 

**The following may still be useful when planning your next data acquisition if you already know that ORB-SLAM3 will need to be used.**

**0. Understanding EuRoc data structure** 

The `Datasets/EuRoc/` directory has the following structure:

```bash
MH01
    └── mav0
        ├── body.yaml
        ├── cam0
        │   ├── data
        │   ├── data.csv
        │   └── sensor.yaml
        ├── cam1
        │   ├── data
        │   ├── data.csv
        │   └── sensor.yaml
        ├── imu0
        │   ├── data.csv
        │   └── sensor.yaml
        ├── leica0
        │   ├── data.csv
        │   └── sensor.yaml
        └── state_groundtruth_estimate0
            ├── data.csv
            └── sensor.yaml

```

- Each of the `camX/data/` folder contains all the `.png` image files for both cameras (stereo). File names are based on their timestamp in nanoseconds, e.g., `1403636763663555584.png` (Jun 24, 2014 at 19:06:03 UTC; epoch Jan 1, 1970).  
- Each `data.csv` file contains a two column tabular structure of the form
    - for cameras: `timestamp, filename` (e.g.,`1403636763463555584,1403636763463555584.png`).
    - for imu: `timestamp, ax, ay, az, gx, gy, gz`
- Each `sensor.yaml` file contains raw sensor calibration data (intrinsics, distorsions, extrinsics, and sensor-specific parameters such as IMU noise and bias characteristics). For example:

```yaml
## cam config file
# General sensor definitions.
sensor_type: camera
comment: VI-Sensor cam0 (MT9M034)

# Sensor extrinsics wrt. the body-frame.
T_BS:
  cols: 4
  rows: 4
  data: [0.0148655429818, -0.999880929698, 0.00414029679422, -0.0216401454975,
         0.999557249008, 0.0149672133247, 0.025715529948, -0.064676986768,
        -0.0257744366974, 0.00375618835797, 0.999660727178, 0.00981073058949,
         0.0, 0.0, 0.0, 1.0]

# Camera specific definitions.
rate_hz: 20
resolution: [752, 480]
camera_model: pinhole
intrinsics: [458.654, 457.296, 367.215, 248.375] #fu, fv, cu, cv
distortion_model: radial-tangential
distortion_coefficients: [-0.28340811, 0.07395907, 0.00019359, 1.76187114e-05]
```


```yaml
## imu config file
#Default imu sensor yaml file
sensor_type: imu
comment: VI-Sensor IMU (ADIS16448)

# Sensor extrinsics wrt. the body-frame.
T_BS:
  cols: 4
  rows: 4
  data: [1.0, 0.0, 0.0, 0.0,
         0.0, 1.0, 0.0, 0.0,
         0.0, 0.0, 1.0, 0.0,
         0.0, 0.0, 0.0, 1.0]
rate_hz: 200

# inertial sensor noise model parameters (static)
gyroscope_noise_density: 1.6968e-04     # [ rad / s / sqrt(Hz) ]   ( gyro "white noise" )
gyroscope_random_walk: 1.9393e-05       # [ rad / s^2 / sqrt(Hz) ] ( gyro bias diffusion )
accelerometer_noise_density: 2.0000e-3  # [ m / s^2 / sqrt(Hz) ]   ( accel "white noise" )
accelerometer_random_walk: 3.0000e-3    # [ m / s^3 / sqrt(Hz) ].  ( accel bias diffusion )
```

```yaml
## state_groundtruth_estimate
# Sensor extrinsics wrt. the body-frame. This is the transformation of the
# tracking prima to the body frame.
T_BS:
  cols: 4
  rows: 4
  data: [1.0, 0.0, 0.0, 0.0,
         0.0, 1.0, 0.0, 0.0,
         0.0, 0.0, 1.0, 0.0,
         0.0, 0.0, 0.0, 1.0]
```
>[!NOTE]
> [Here](/config/) you will find a couple of examples of the config files I used to run the SPICE-HL3 dataset in monocular, stereo, and their inertial variants using the ZED2 camera data. **Note** that while I believe those were the last two config file versions I used to run it succesfully, some tweaking on your part may still be required.

**1. File naming**

I had to modify the file name convention to match that of the EuRoc dataset: to go from `stereo_left_1726153517.476212590_0.png` (with timestamp in seconds) to `timestamp.png` (with timestamp in nanoseconds). 

For this, I created a script called [rename_data](/tools/rename_data.py) that renames all the `cam0` and `cam1` files accordingly.

**2. Generate data files** 

I wrote a second script called [generate_csv](/tools/generate_csv.py) to create the `data.csv` files for each camera by extracting timestamps and filenames from the newly renamed files.  

I wrote the script `convert_imu_csv.py` to adapt the `data.csv` for the IMU as well. In this case, EuRoc creates a CSV file with the followign columns `Timestamp (ns) | wx (rad/s) | wy (rad/s) | wz (rad/s) | ax (m/s^2) | ay (m/s^2) | ay (m/s^2) | az (m/s^2)`. See an example row below:

```
1403636579758555392,-0.099134701513277898,0.14730578886832138,0.02722713633111154,8.1476917083333333,-0.37592158333333331,-2.4026292499999999
```

Whereas the SPICE-HL2 IMU data is saved in the following way `Time (s) | OrientationX | OrientationY  | OrientationZ | OrientationW | Angular_VelX (rad/s) | Angular_VelY (rad/s) | Angular_VelZ (rad/s) | Linear_AccX (m/s^2) | Linear_AccY (m/s^2) | Linear_AccZ (m/s^2) |Orientation Covariance | Velocity Covariance | Acceleration Covariance`. 

Lastly, I need to use info contained in the previous individual config files to build a high-level dataset config wrapper file `spice-hl3.yaml` file. This file should be adapted from the `EuRoC.yaml` configuration file. More info on this dataset configuration file [here](./orbslam3_explained.md#orb-slam3-configuration-file).

**3. Main timestamps file**

For the main EuRoC timestamps file (e.g., `./Examples/Monocular-Inertial/EuRoC_TimeStamps/MH01.txt`), it looks like timestamps are taken from the left camera `data.csv`. 

I created the new `trajectory_F.txt` file from spice-hl3's `cam0/data.csv` file using the [extract_timestamps](/tools/extract_timestamps.py) script.

**4. Mismatching timestamps** 

I need to ensure data is synchronized properly, i.e., left and right images must be taken at the same time (or very close) and IMU data must be well-timed and match with image timestamps (interpolation may be needed otherwise).

>[!CAUTION]
> There is a total of 646 missing or mismatched timestamps between `cam0`and `cam1`in the `spice-hl3` dataset (most likely associated to ROS2 timing issues). I need to ensure both camera data are synchronized by timestamp; one image per timestamp from each camera.

To remove all unmatched timestamped frames from left and right I used the [missing_frames.py](/tools/missing_frames.py) script.

>**RESULTS FOR 10ms DIFFERENCE**
> Total missing or mismatched timestamps: 646
> Total closest timestamps found: 33
> Cam0 Stats:
>     Avg frame interval: 0.097036 s
>     Frame rate: 10.31 FPS
>     Interval std deviation: 0.102444 s
> Cam1 Stats:
>     Avg frame interval: 0.097036 s
>     Frame rate: 10.31 FPS
>     Interval std deviation: 0.102444 s

### Testing new data

For testing ORB-SLAM3 on the new data, I need to make the spice-hl3 directory I just created in host available within the container. I transferred the directory to the existing container with

```
docker cp /path/on/host your-container:/path/in/container
```

Later on I could always mount it as a new volume for the final release. 

Run ORB-SLAM on a short part of my own dataset. Check:
- initialization success
- trajectory ouput
- tracking stability

## Docker commands

Here's my own cheatsheet of docker commands:

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

docker exec -it container-name /bin/bash #open a new terminal within a container (to open more than one terminal)
docker exec -it container-name ls #run other commands inside a container, in this case 'ls'

# how to access and work on files outside the container
# assume we have a local directory called source/something.py
docker run -it -v $PWD/source:/my_source_code image-name # my_source_code is how the directory source will be named inside the docker image (the copy of the folder will be renamed as my_source_code)

docker cp <container_id>:/path/in/container/file.txt /host/destination/ #copy files or directories form container to host

```

## Things to improve

- [x] build the docker image 
- [x] run the container
- [x] debug with euroc mh01 dataset
- [ ] build ORB-SLAM3 from the Dockerfile instead of manually building it within the container.
- [x] learn about creating a non-root user
- [x] learn about adding sudo to docker
- [x] adapt my own data to work with ORBSLAM3
- [x] mount a volume to place output trajectories so they are accessible from host
- [x] (optional) add a `docker-compose.yml` file to run it including local datasets, any custom config files...
- [x] (optional) a launch script `run_docker.sh` --> how would this work? how is it different from docker-compose? --> written but haven't used it yet. not sure I need the permissions line.
- [ ] (optional) define an `entrypoint.sh`. File written but unused yet. 
- [ ] (optional) how to include GPU support (CUDA)
- [ ] try it out on Win terminal
- [ ] adapt to other common datasets
- [x] adapt to spice hl3
- [ ] create a auto-download script for spice-hl3
- [x] adapt evaluation script to matlab
- [ ] adapt evaluation script to py3