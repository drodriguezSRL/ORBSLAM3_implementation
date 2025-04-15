# === Dockerfile ===
# Production-ready Dockerfile for ORB-SLAM3 based on Kevin Robb's setup

FROM ubuntu:20.04

# Set working directory
WORKDIR /root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \ 
    cmake \ 
    git \
    libgtk2.0-dev \ 
    libavcodec-dev \ 
    libavformat-dev \
    libswscale-dev \
    libtbb2 \ 
    libtbb-dev \ 
    libjpeg-dev \ 
    libpng-dev \ 
    libtiff-dev \
    libdc1394-22-dev \ 
    libglew-dev \ 
    libboost-all-dev \ 
    libssl-dev \
    libeigen3-dev \
    libcanberra-gtk-module \ 
    libatlas-base-dev \
    libsuitesparse-dev \
    pkg-config \
    python3-dev \ 
    python3-pip \
    python3-venv \
    unzip\
    wget && \ 
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages globally
COPY py-requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r py-requirements.txt

# Install Pangolin (specific commit)
# 1- create a build directory
WORKDIR /root/Dev
# 2- clone the Pangolin repository
RUN git clone https://github.com/stevenlovegrove/Pangolin.git && \
    cd Pangolin && \
    git checkout 86eb4975fc4fc8b5d92148c2e370045ae9bf9f5d && \
    mkdir build && \
    cd build && \
    cmake .. _DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    make install

# Install OpenCV 4.2.0 
# use same workdir as pangolin
# clone the opencv repository and install the 4.2.0 version
RUN git clone https://github.com/opencv/opencv.git  opencv4 &&\
    cd opencv4 && \
    git checkout 4.2.0 && \
    sed -i '1i\ #define AV_CODEC_FLAG_GLOBAL_HEADER (1 << 22)\n#define CODEC_FLAG_GLOBAL_HEADER AV_CODEC_FLAG_GLOBAL_HEADER\n#define AVFMT_RAWPICTURE 0x0020' modules/videoio/src/cap_ffmpeg_impl.hpp && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=Release -D WITH_CUDA=OFF -D CMAKE_INSTALL_PREFIX=/usr/local .. && \    
    make -j$(nproc) && \
    make install

# Install OpenCV 3.2.0
# use same workdir as pangolin
# clone the opencv repository and install the 3.2.0 version 
RUN git clone https://github.com/opencv/opencv.git opencv3 && \
    cd opencv3 && \
    git checkout 3.2.0 && \
    sed -i '1i\ #define AV_CODEC_FLAG_GLOBAL_HEADER (1 << 22)\n#define CODEC_FLAG_GLOBAL_HEADER AV_CODEC_FLAG_GLOBAL_HEADER\n#define AVFMT_RAWPICTURE 0x0020' modules/videoio/src/cap_ffmpeg_impl.hpp && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=Release -D WITH_CUDA=OFF -D CMAKE_INSTALL_PREFIX=/usr/local .. && \
    make -j$(nproc) &&\
    make install

# Clone and build ORB_SLAM3
# same workdir /root/Dev
# 1. clone and checkout specific commit (an older version of orbslam3)
RUN git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git && \
    cd ORB_SLAM3 && \
    git checkout ef9784101fbd28506b52f233315541ef8ba7af57
WORKDIR /root/Dev/ORB_SLAM3
# this version appears to have some compilation errors that need to be fixed:
# 2. fix line in LoopClosing.h
RUN sed -i '51s|Eigen::aligned_allocator<std::pair<const KeyFrame\*, g2o::Sim3> > > KeyFrameAndPose;|Eigen::aligned_allocator<std::pair<KeyFrame *const, g2o::Sim3> > > KeyFrameAndPose;|' ./include/LoopClosing.h
# 3. fix OpenCV version in CMakeLists.txt
RUN sed -i 's/find_package(OpenCV REQUIRED)/find_package(OpenCV 3.2)/' CMakeLists.txt
# 4. fix uninitialized pointer issue in System.cc (2 locations)
RUN sed -i '584s|Map\* pBiggerMap;|Map* pBiggerMap = nullptr;|' ./src/System.cc && \
    sed -i '701s|Map\* pBiggerMap;|Map* pBiggerMap = nullptr;|' ./src/System.cc
# NOTE: This latter error allowed the examples to run fine, but they caused a segmentation fault at the very end when trying to save the map.
# 5. build the project (retry if needed)
# NOTE: It will likely show errors. So I just run it 5 times without changing anything, hoping it should succeed after a few attempts. I capture build logs for debugging in build_log.txt just in case.
RUN chmod +x build.sh && \
    bash -c '\
    for i in {1..5}; do \
        echo "Build attempt #$i";\
        ./build.sh >> build_log.txt 2>&1 && break || sleep 5; \
    done' 


# Set the default command to bash
CMD ["bash"]
