# ORB-SLAM3 Explained

This file is intended to explain things related to what ORB-SLAM3 does in the background. 

## Commands to run examples

As explained in the [README](/README.md) file, the following command line is needed to run the stereo example from the EuRoC MH01 dataset: 

```
./Examples/Stereo/stereo_euroc ./Vocabulary/ORBvoc.txt ./Examples/Stereo/EuRoC.yaml ~/Datasets/EuRoc/MH01 ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt dataset-MH01_stereo
```

- `./Examples/Stereo/stereo_euroc`: this runs the executable for the stereo version of ORB-SLAM3 over the EuRoC dataset. This executable was previously compiled from the ORB-SLAM3 source code during build. 
- `./Vocabulary/ORBvoc.txt`: this the first command-line argument passed directly to the executable. It tells it to use a pre-trained ORB vocabulary to aid in future matching and place recognition (loop closure).
- `./Examples/Stereo/EuRoC.yaml`: second command-line argument includes all a configuration file with all the camera parameters (intrinsics, extrinsics, distorsion, stereo baseline, etc.).
- `~/Datasets/EuRoc/MH01`: third command-line argument defines the path to the dataset folder containing in this case data for the left and right stereo cameras. 
- `./Examples/Stereo/EuRoC_TimeStamps/MH01.txt`: fourth command-line argument contains the timestamps of each stereo image pair. It is used to synchronize and load frames in the correct temporal order.
- `dataset-MH01_stereo`: last command-line argument includes the name of the output folder/sequence name. 

## ORB-SLAM3 Keyframes

Keyframes are the core structure of the map in SLAM systems. While normal frames are only used for tracking the current camera pose, keyframes are used for 3D map point creation and triangulation, loop closure, global optimization, and relocalization (if tracking is lost, keyframes are used to recover).  

Keyframes are stored permanently (until culled) and connected in a co-visibility graph; i.e., a data structure that links keyframes sharing many 3D map points. Keyframes are used to improve memory usage, speeding up loop closure, and make optimization more efficient. 

So in summary, the system processes every frame for pose tracking, but only promotes important ones to keyframes to build and maintain the map efficiently. 

ORB-SLAM3 uses several criteria to decide whether a new frame should be flagged as a keyframe:

1. **Parallax/motion change**: has the camera moved enough since the last keyframe? (this might be a new view)
2. **Number of tracked map points**: is the current frame tracking too few 3D map points from the last keyframe? (if so, this might be a new unseen area)
3. **Feature match quality**: is the number of matched features too low? (same logic, might be a new unseen area)
4. **Temporal heuristics**: has too much time passed since the last keyframe? (avoid large temporal gaps between keyframes)
5. **Loop closure or relocalization events**: has a loop-closure or relocalization been detected? (if so, insert a keyframe to stabilize and anchor the new pose)
6. **Sensor-specific logic**: depends on the sensor used we may flag more or less frames as keyframes (e.g., monocular is more conservative than stereo in adding keyframes)

## Output files

ORB-SLAM3 generates 2 output files:

**f_dataset-name_sequence.txt**

This file contains the camera poses for every frame (or image pair) processed during the run. It includes both tracked fgrames and possibly los frames (interpolated or untracked). 

This is useful for evaluating full motion over time. 

It contains dense data; i.e., 1 line per frame. Each line contains `timestamp tx ty tz qx qy qz qw` (`t*`: translation, `q*`: quaternion). See example below. 

```
1403636762713555456.000000 -0.183154613 0.301140279 0.143953711 -0.016206501 -0.114830762 -0.021424215 0.993021786
```

This file is useful for full trajectory evaluations and comparison against ground truth files. 

**kf_dataset-name_sequence.txt**

This file contains the poses of only the keyframes selected by ORB-SLAM3 during the run. 

Keyframes are important frames selected for creating the map structure (and used for loop closure and back-end optimization processes, including map building). For more info on keyframes check [ORB-SLAM3 Keyframes](#orb-slam3-keyframes). 

It has the same file structure as the frame trajectory output file: one line per keyframe, which includes timestamps, translation, and quaternion values for each keyframe.   

This file is useful to evaluate the map structure and analyze graph optimization (how the system made decisions).