# How was ORBSLAM3_implementation done

This describes how this ORBSLAM3 docker implementation was done. It includes all the bugs and workarounds that were needed to make it work.
The goal of this file is to leave a record of everything that's behind the scenes of this repository. 
I used this file as a log book of every step I took (and planned on taking, thus the present tense used at times) during development. 


Since this was one of the first times for me working intensively with Docker, I created my own cheatlist of Docker commands, which, in case you are a newbie like me, can be found [here](#docker-commands). 

## Phase 1: Environment setup

### Install a fresh Ubuntu 20.04

I'm going to run Ubuntu on [Windows Subsytem for Linux (WSL)](https://documentation.ubuntu.com/wsl/en/latest/) instead than on a virtual machine like VMware Workstation. 

WSL enables us to run a GNU/Linux environment on Windows. Once installed, Ubuntu can be used as a terminal interface on Windows and can launch any linux-native applications.

If you don't have the latest WSL install you can run in the command line as administrator the following:

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

Optionally we can (re)build the image and start the container all at once with `docker-compose up`. To do this in the background (aka 'detached mode') (e.g., ROS2 + GPU + SLAM pipeline) with:

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

The third thing we need is giving it an X display by setting up the X environment variable. We can tell docker to use the same one the host is using `--env=DISPLAY`. I included this argument within my `docker-compose.yml` environment as `DISPLAY=${DISPLAY}`. 

>[!TIP]
> We can also run the container as a user that has permision to access X display, e.g., run the container as a user that matches the host. 

**Success**: name of the current container `docker-orbslam3-spell-run-ee6c1ca75dba`.

## Phase 4: Comparing results for example case

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

**B. Manually copy the files from the container to a directory in the host**

Since option A would require re-running the container (starting fresh), I could instead use `docker cp` to copy files from container to host. Running a command like:

```
docker cp <container_id>:/path/in/container/file.txt /host/destination/
```

Independently from which of these two options I choose (A or B), ORB-SLAM3 provides a script to evaluate the generated trajectory against the ground truth. This script can be found in `~/Dev/ORB_SLAM3/evaluation/evaluate_ate_scale.py`.

>[!IMPORTANT]
> From [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3): it should be noted that EuRoC provides ground truth for each sequence in the IMU body reference. As pure visual executions report trajectories centered in the left camera, the script `evaluate_ate_scale.py` provides in the "evaluation" folder the transformation of the ground truth to the left camera reference. Visual-inertial trajectories use the ground truth from the dataset.


## Phase 5: Adapting my own data

I'm going to try to adapt the [SPICE-HL3 dataset](https://github.com/spaceuma/spice-hl3) to work with ORB-SLAM3.

The best strategy would be to try to emulate the layout and setup of the working example whose sensor configuration matches that of the new dataset. In this case that would be the Stereo+IMU configuration. 

Make sure you understand the parsing of arguments when running the `stereo_inertial_euroc` example. More info [here](/orbslam3_explained.md). As a summary, we have:

1. Executable wrapper: `stereo_inertial_euroc.cc` 
2. Vocabulary: `ORBvoc.txt`
3. Configuration: `EuRoc.yaml`
4. Path to dataset: `~/Datasets/EuRoc/MH01`
5. Timestamps: `MH01.txt`
6. Output file name: `dataset-MH01_stereoi`

### Adapting the executable

I'm going to copy and adapt the `./Examples/Stereo-Inertial/stereo_inertial_euroc.cc` script to work with my own data. 

First thing I will need to do is to create a new directory, which I will create in the ' /data' folder that is later on mount to `~/Datasets`, that micmicks what's inside the docker at `~/Dev/ORB_SLAM3/Examples/`. This new directory will be called `spice-hl3`. 

In this directory I will have to include the following:

```bash
spice-hl3
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
    ├── spice-hl3.yaml
    ├── stereo_inertial_spicehl3.cc
    └── spicehl3_TimeStamps 
        ├── trajectoryA.txt
        ├── trajectoryB.txt
        ├── ...
        └── trajectoryG.txt
```

I need to modify the file name convention to match that of the EuRoc dataset: to go from `stereo_left_1726153517.476212590_0.png` (with timestamp in seconds) to `timestamp.png` (with timestamp in nanoseconds). For this, I created a [script](/tools/rename_data.py) that renames all the `cam0` and `cam1` files accordingly.

Then I need to create the `stereo_inertial_spicehl3.cc` from the original EuRoc executable. 

- [ ] create spice-hl3 directory and transfer data
- [ ] adapt data formatting 
- [ ] copy and adapt executable

### ORB-SLAM3 vocabulary

I will use the same one located at `~/Dev/ORB_SLAM3/Vocabulary/ORBvoc.txt`. 

### Dataset configuration file

ORB-SLAM3 requires loading a high-level dataset config wrapper file, e.g., `EuRoc.yaml`. This configuration file is written specifically to work with ORB-SLAM3. Contains only the subset of calibration and config values that ORB-SLAM3 needs:

- Camera instrinsics
- Distortion parameters
- Camera resolution
- IMU-to-camera extrinsics (`Tcb`)
- IMU noise parameters (for preintegration)

This file must be formatted specifically for ORB-SLAM3, using OpenCV YAML format and with specific keys it expects (e.g., `Camera.fx`, `IMU.noise_gyro`, etc.).

- [ ] create high-level config file

In the case of EuRoc, this is what `EuRoc.yaml` contains: 

```yaml
%YAML:1.0

#--------------------------------------------------------------------------------------------
# Camera Parameters. Adjust them!
#--------------------------------------------------------------------------------------------
Camera.type: "PinHole"

# Camera calibration and distortion parameters (OpenCV) (equal for both cameras after stereo rectification)
Camera.fx: 435.2046959714599
Camera.fy: 435.2046959714599
Camera.cx: 367.4517211914062
Camera.cy: 252.2008514404297

Camera.k1: 0.0
Camera.k2: 0.0
Camera.p1: 0.0
Camera.p2: 0.0

Camera.width: 752
Camera.height: 480

# Camera frames per second
Camera.fps: 20.0

# stereo baseline times fx
Camera.bf: 47.90639384423901

# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
Camera.RGB: 1

# Close/Far threshold. Baseline times.
ThDepth: 35.0 # 35

# Transformation from camera 0 to body-frame (imu)
Tbc: !!opencv-matrix
   rows: 4
   cols: 4
   dt: f
   data: [0.0148655429818, -0.999880929698, 0.00414029679422, -0.0216401454975,
         0.999557249008, 0.0149672133247, 0.025715529948, -0.064676986768,
        -0.0257744366974, 0.00375618835797, 0.999660727178, 0.00981073058949,
         0.0, 0.0, 0.0, 1.0]

# IMU noise
IMU.NoiseGyro: 1.7e-04 # 1.6968e-04
IMU.NoiseAcc: 2.0e-03 # 2.0000e-3
IMU.GyroWalk: 1.9393e-05
IMU.AccWalk: 3.e-03 # 3.0000e-3
IMU.Frequency: 200

#--------------------------------------------------------------------------------------------
# Stereo Rectification. Only if you need to pre-rectify the images.
# Camera.fx, .fy, etc must be the same as in LEFT.P
#--------------------------------------------------------------------------------------------
LEFT.height: 480
LEFT.width: 752
LEFT.D: !!opencv-matrix
   rows: 1
   cols: 5
   dt: d
   data:[-0.28340811, 0.07395907, 0.00019359, 1.76187114e-05, 0.0]
LEFT.K: !!opencv-matrix
   rows: 3
   cols: 3
   dt: d
   data: [458.654, 0.0, 367.215, 0.0, 457.296, 248.375, 0.0, 0.0, 1.0]
LEFT.R:  !!opencv-matrix
   rows: 3
   cols: 3
   dt: d
   data: [0.999966347530033, -0.001422739138722922, 0.008079580483432283, 0.001365741834644127, 0.9999741760894847, 0.007055629199258132, -0.008089410156878961, -0.007044357138835809, 0.9999424675829176]
LEFT.Rf:  !!opencv-matrix
   rows: 3
   cols: 3
   dt: f
   data: [0.999966347530033, -0.001422739138722922, 0.008079580483432283, 0.001365741834644127, 0.9999741760894847, 0.007055629199258132, -0.008089410156878961, -0.007044357138835809, 0.9999424675829176]
LEFT.P:  !!opencv-matrix
   rows: 3
   cols: 4
   dt: d
   data: [435.2046959714599, 0, 367.4517211914062, 0,  0, 435.2046959714599, 252.2008514404297, 0,  0, 0, 1, 0]

RIGHT.height: 480
RIGHT.width: 752
RIGHT.D: !!opencv-matrix
   rows: 1
   cols: 5
   dt: d
   data:[-0.28368365, 0.07451284, -0.00010473, -3.555907e-05, 0.0]
RIGHT.K: !!opencv-matrix
   rows: 3
   cols: 3
   dt: d
   data: [457.587, 0.0, 379.999, 0.0, 456.134, 255.238, 0.0, 0.0, 1]
RIGHT.R:  !!opencv-matrix
   rows: 3
   cols: 3
   dt: d
   data: [0.9999633526194376, -0.003625811871560086, 0.007755443660172947, 0.003680398547259526, 0.9999684752771629, -0.007035845251224894, -0.007729688520722713, 0.007064130529506649, 0.999945173484644]
RIGHT.P:  !!opencv-matrix
   rows: 3
   cols: 4
   dt: d
   data: [435.2046959714599, 0, 367.4517211914062, -47.90639384423901, 0, 435.2046959714599, 252.2008514404297, 0, 0, 0, 1, 0]

#--------------------------------------------------------------------------------------------
# ORB Parameters
#--------------------------------------------------------------------------------------------

# ORB Extractor: Number of features per image
ORBextractor.nFeatures: 1200

# ORB Extractor: Scale factor between levels in the scale pyramid
ORBextractor.scaleFactor: 1.2

# ORB Extractor: Number of levels in the scale pyramid
ORBextractor.nLevels: 8

# ORB Extractor: Fast threshold
# Image is divided in a grid. At each cell FAST are extracted imposing a minimum response.
# Firstly we impose iniThFAST. If no corners are detected we impose a lower value minThFAST
# You can lower these values if your images have low contrast
ORBextractor.iniThFAST: 20
ORBextractor.minThFAST: 7

#--------------------------------------------------------------------------------------------
# Viewer Parameters
#--------------------------------------------------------------------------------------------
Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1
Viewer.GraphLineWidth: 0.9
Viewer.PointSize:2
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3
Viewer.ViewpointX: 0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -1.8
Viewer.ViewpointF: 500
```

### Understanding EuRoc data structure 

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

- Each of the `camX/data/` folders contain all the `.png` image files for both cameras (stereo). File names are based on their timestamp in nanoseconds, e.g., `1403636763663555584.png` (Jun 24, 2014 at 19:06:03 UTC; epoch Jan 1, 1970).  
- Each `data.csv` file contains a two column tabular structure of the form
    - for cameras: `timestamp, filename` (e.g.,`1403636763463555584,1403636763463555584.png`).
    - for imu: `timestamp, ax, ay, az, gx, gy, gz`
- Each `sensor.yaml` file contains raw sensor calibration data (intrinsics, distorsions, extrinsicsm and sensor-specific parameters such as IMU noise and bias characteristics). For example:

**cam config file** 

```yaml
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

**imu config file** 
```yaml
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

**state_groundtruth_estimate** 
```yaml
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

>[!IMPORTANT]
> Ensure data is synchronized properly, i.e., left and right images must be taken at the same time (or very close) and IMU data must be well-timed and match with image timestamps (interpolation may be needed otherwise).




Run ORB-SLAM on a short part of my own dataset. Check
- initialization success
- trajectory ouput
- tracking stability



## Phase X: What's next...

Things I still need to do:

- [x] build the docker image 
- [x] run the container
- [x] debug with euroc mh01 dataset
- [x] how to build ORBSLAM3 from within the Dockerfile
- [x] learn about creating a non-root user
- [x] learn about adding sudo to docker
- [ ] learn about adapting my own data to work with ORBSLAM3
- [x] mount a volume to place output trajectories so they are accessible from host
- [x] (optional) add a `docker-compose.yml` file to run it including local datasets, any custom config files...
- [x] (optional) a launch script `run_docker.sh` --> how would this work? how is it different from docker-compose? --> written but haven't used it yet. not sure I need the permissions line.
- [ ] (optional) what is `entrypoint.sh` for? how could I use it?
- [ ] (optional) how to include GPU support (CUDA)
- [ ] try it out on windows terminal
- [ ] adapt to other common datasets
- [ ] adapt to spice hl3

next step: adapting data to work with orbslam3...


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

docker cp <container_id>:/path/in/container/file.txt /host/destination/ #copy files or directories form container to host

```