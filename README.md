# ORBSLAM3_implementation
This contains a working Docker implementation of ORB-SLAM3. This implementation is heavily based on [Kevin Robb's](https://github.com/kevin-robb/orb_slam_implementation).

Original ORB-SLAM3 repo: [https://github.com/UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) 
Original repo was last updated: Dec 2021
Check [orbslam3_explained](/orbslam3_explained.md) for useful details on ORB-SLAM3. 

For a exhaustive description of how this implementation was developed and a list of what still remains to be implemented, check [how_was_it_made](how_was_it_made.md).

## Step 1: Setup

Clone this repository

```
git clone https://github.com/drodriguezSRL/ORBSLAM3-implementation
```

Run the dataset setup script. This downloads, unzips, and fixes the EuRoC dataset (some images may be corrupted and cause problems down the line) and places it in `./data/EuRoc`.

```
cd ORBSLAM3-implementation
bash download_euroc_mh01.sh
```

Build and run the Dockerfile through docker-compose
```
cd docker
docker-compose build 
docker-compose run orbslam3-spell
```

## Step2: Build ORB-SLAM3

In its current version, the Docker container includes a cloned and fixed workspace but unbuilt version of ORB-SLAM3. We need to manually build it inside the container. 

Within the container, run the following command:

```
cd ~/Dev/ORB_SLAM3
sh build.sh
```

>[!IMPORTANT]
> As indicated by [Kevin Robb's implementation instructions](https://github.com/kevin-robb/orb_slam_implementation), ORB-SLAM3 requires multiple build runs before it can be succesfully built without any errors or warnings. In my experience, it often required between 3 to 5 builds (i.e, running the `sh build.sh` command multiple times) before it was successfully built. 

## Step 3: Run examples

Once ORB-SLAM3 is built, we can run a few simulation examples from the EuRoc dataset previously downloaded. 

Within the container, change to the `~/Dev/ORB_SLAM3/` directory, and choose one of the following to run. A map viewer as well as an image viewer should appear during the simulation. Once done, a `f_dataset-MH01_...txt` and a `kf_dataset-MH01_...txt` files are created within the `ORB_SLAM3` folder containing the camera complete estimated trajectory and keyframe trajectory, respectively. 

For a detail description of these ORB-SLAM3 commands, check [orbslam3_explained](./orbslam3_explained.md). 

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

![Image](/docs/images/orbslam_euroc_mono.gif)

## Step 4: Adapt your own data 

The most straigthforward solution for making your own data work with ORB-SLAM3 would be to mimick as much as possible the directory layout and data structure of one of the working examples provided by the original ORB-SLAM3 implementation. Then, you'd simply need to call the pre-existing executable of your choosing (mono, mono-interial, stereo, or stereo-inertial) in a similar fashion as did before. 

In my case, I chose to use the EuRoC data structure as a reference. Since making a one-size-fits-all guide for data adaption would be almost impossible (as it would depend on the nature of your own data to begin with), you can check [here](/how_was_it_made.md#phase-5-adapting-my-own-data) all the steps I followed to run ORB-SLAM3 on the [SPICE-HL3 dataset](https://github.com/spaceuma/spice-hl3). 

