# ORB-SLAM3 Explained

This file is intended to explain what ORB-SLAM3 does in the background. 

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
- `dataset-MH01_stereo`: last command-line argument includes the name of the output sequence name. These will be used to name the two output files (i.e., `f_dataset-MH01_stereo.txt` and `kf_dataset-MH01_stereo.txt`).

>[!NOTE]
> For details on ORB-SLAM3 executables, check [Executables](#executables). 

## ORB-SLAM3 Keyframes

Keyframes are the core structure of the map in SLAM systems. While normal frames are only used for tracking the current camera pose, keyframes are used for 3D map point creation and triangulation, loop closure, global optimization, and relocalization (if tracking is lost, keyframes are used to recover).  

Keyframes are stored permanently (until "culled"; i.e. removed) and connected in a co-visibility graph; i.e., a data structure that links keyframes sharing many 3D map points. Keyframes are used to improve memory usage, speeding up loop closure, and make optimization more efficient. 

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

This file contains the camera poses for every frame (or image pair) processed during the run. It includes both tracked fgrames and possibly lost frames (interpolated or untracked). 

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

## Executables

Exectuables, such as `stereo_euroc.cc`, are used by ORB-SLAM3 to setup the environment for demos (aka "demo wrappers"), load data, and call into the real core of the SLAM system, which is implemented in the [ORB-SLAM3 library code](#orb-slam3-library-code).

An example of an ORB-SLAM3 stereo executable can be found inside the docker under `ORB_SLAM3/Examples/Stereo`. 

The file `stereo_euroc.cc` executable is used to run stereo visual SLAM on the EuRoC dataset. These executables are compiled the during the ORB-SLAM3 build.

The purpose of this executable is to:
1. Load stereo image sequences and timestamps from EuRoC dataset folders.
2. Load calibration parameters and rectify the images using these parameters.
3. Feed them into ORB-SLAM3 for stereo tracking.
4. Optionally save the resulting trajectories.

## ORB-SLAM3 library code

The core source code of the ORB-SLAM3 system is located in the main `src` and `include` directories. In `src` is where the actual ORB-SLAM3 algorithmic logic lives. The directory `include` hosts all the header files (`*.h`) required for the `*.cc` files in `src`.

The main entry point to the ORB-SLAM3 is the `system.cc` file. It manages all subsystems (tracking, mapping, loop closing, etc.) and provides the key method, `SLAM.TrackStereo()`, which internally invokes the pipeline. 

Here's a simplified example of what happens when you call `SLAM.TrackStereo()`:

1. `System::TrackStereo()`
2. `Tracking::GrabImageStereo()`
3. `Tracking::Track()`
4. (inside Track):
    - ORB extraction
    - Feature matching
    - Pose estimation (PnP, motion model)
    - Decision to add keyframe
5. Keyframe passed to:
    - `LocalMapping` for backend optimization
    - `LoopClosing` for loop detection

The following lists some of the key classes contained in ORB-SLAM3 source code:

- `Tracking.cc`: contains the core SLAM pipeline logic and the heart of the frontend, including ORB feature extraction, frame tracking, pose estimation, keyframe decision-making, triangulation, and IMU integration (if used). 
- `LocalMapping.cc`: running in a separate thread, it handles local bundle adjustment, new map point creation, and keyframe insertion logic (part of the backend)
- `LoopClosing.cc`: another separate thread, responsible for detecting loops (revisiting previous locations), computing similarity transforms, and performing pose graph optimization.
- `Map.cc`/`MapPoint.cc`/`KeyFrame.cc`: these classes manage the global map structure, the storage of 3D points and keyframes, and the graph structure (covisibility, spanning tree).
- `Frame.cc`/`KeyFrame.cc`: they contain logic for feature matching, pose prediction, motion models, and IMU propagation (if applicable).
- `Optimizer.cc`: implements bundle adjustment, pose graph opitmization, and g2o-based SLAM backend logic.
- `ORBextractor.cc`: implements the ORB feature detection and description (FAST + BRIEF with orientation and scale invariance).

## ORB-SLAM3 configuration file

ORB-SLAM3 requires loading a high-level dataset config wrapper file, e.g., `EuRoc.yaml`. This configuration file is written specifically to work with ORB-SLAM3. Contains only the subset of calibration and config values that ORB-SLAM3 needs:

- Camera instrinsics
- Distortion parameters
- Camera resolution
- IMU-to-camera extrinsics (`Tcb`)
- IMU noise parameters (for preintegration)

This file must be formatted specifically for ORB-SLAM3, using OpenCV YAML format and with specific keys it expects (e.g., `Camera.fx`, `IMU.noise_gyro`, etc.).

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

# Transformation from camera 0 to body-frame ()
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