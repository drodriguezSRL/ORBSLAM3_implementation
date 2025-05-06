# ORBSLAM3_implementation
This contains a working Docker implementation of ORB-SLAM3. This implementation is heavily based on [Kevin Robb's](https://github.com/kevin-robb/orb_slam_implementation).

Original ORB-SLAM3 repo: [https://github.com/UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) 
Original repo was last updated: Dec 2021

For a exhaustive description of how this implementation was developed and a list of what still remains to be implemented, check [how_was_it_made](how_was_it_made.md).

## Step 1: Setup

Clone this repository

```
git clone https://github.com/drodriguezSRL/ORBSLAM3-implementation
```

Run the dataset setup script. This downloads, unzips, and fixes the EuRoC dataset and places it (say) in `~/Datasets/EuRoc/MH01`.

```
bash download_euroc_mh01.sh
```

Build and run the Dockerfile through docker-compose
```
cd docker
docker-compose build 
docker-compose run orbslam3-spell
```

## Step2: Build ORB-SLAM3

In its current version, the Docker container includes a cloned and fixed repository but unbuilt version of ORB-SLAM3. We need to build it inside the container. 

Within the container, run the following command:

```
cd ~/Dev/ORB_SLAM3
sh build.sh
```

>[!IMPORTANT]
> As indicated by Kevin Robb's implementation instructions, ORB-SLAM3 requires multiple builds before it can be succesfully built without any errors or warnings. In my experience, it often required between 3 to 5 builds (i.e, running the `sh build.sh` command) before it was successfully built. 

## Step 3: Run examples

Once ORB-SLAM3 is built, we can run a few simulation examples from the EuRoc dataset previously downloaded. 

Within the container, choose one of the following ro tun. A map viewer as well as an image viewer should appear during the simulation. Once done, a `f_dataset-MH01_...txt` and a `.txt` files are creating containing the camera complete estimated trajectory and keyframes trajectory, respectively. 

```
# Mono
./Examples/Monocular/mono_euroc ./Vocabulary/ORBvoc.txt ./Examples/Monocular/EuRoC.yaml ~/Datasets/EuRoc/MH01 ./Examples/Monocular/EuRoC_TimeStamps/MH01.txt dataset-MH01_mono

# Mono + Inertial
./Examples/Monocular-Inertial/mono_inertial_euroc ./Vocabulary/ORBvoc.txt ./Examples/Monocular-Inertial/EuRoC.yaml ~/Datasets/EuRoc/MH01 ./Examples/Monocular-Inertial/EuRoC_TimeStamps/MH01.txt dataset-MH01_monoi

# Stereo
./Examples/Stereo/stereo_euroc ./Vocabulary/ORBvoc.txt ./Examples/Stereo/EuRoC.yaml ~/Datasets/EuRoc/MH01 ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt dataset-MH01_stereo

# Stereo + Inertial
./Examples/Stereo-Inertial/stereo_inertial_euroc ./Vocabulary/ORBvoc.txt ./Examples/Stereo-Inertial/EuRoC.yaml ~/Datasets/EuRoc/MH01 ./Examples/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt dataset-MH01_stereoi
```

![Image](docs/images/orbslam3_examples_mapviewer.png)

![Image](docs/images/orbslam3_examples_imageviewer.png)

