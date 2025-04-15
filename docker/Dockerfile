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

# Install OpenCV 3.2.0 (ORB-SLAM3 compatible)
RUN wget -q https://github.com/opencv/opencv/archive/3.2.0.zip && \
    unzip 3.2.0.zip && cd opencv-3.2.0 && \
    mkdir build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D WITH_TBB=ON \
          -D BUILD_NEW_PYTHON_SUPPORT=ON \
          -D WITH_V4L=ON \
          -D INSTALL_C_EXAMPLES=ON \
          -D INSTALL_PYTHON_EXAMPLES=ON \
          -D BUILD_EXAMPLES=ON .. && \
    make -j$(nproc) && make install && ldconfig

# Clone and build ORB_SLAM3 (specific commit)
RUN git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git && \
    cd ORB_SLAM3 && git checkout ef9784101fbd28506b52f233315541ef8ba7af57 && \
    sed -i '51s/std::map/std::map<KeyFrame \*const, g2o::Sim3, std::less<KeyFrame \*const>, Eigen::aligned_allocator<std::pair<KeyFrame \*const, g2o::Sim3> > >/' src/LoopClosing.h && \
    sed -i 's/find_package(OpenCV 4.2)/find_package(OpenCV 3.2)/' CMakeLists.txt && \
    sed -i '584s/^/Map\* pBiggerMap = nullptr;\n/' src/System.cc && \
    sed -i '701s/^/Map\* pBiggerMap = nullptr;\n/' src/System.cc && \
    chmod +x build.sh && ./build.sh

# Set the default command to bash
CMD ["bash"]
