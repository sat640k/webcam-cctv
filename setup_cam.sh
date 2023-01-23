#!/bin/bash



sudo apt update
sudo apt upgrade
sudo apt install -y automake build-essential cmake libatlas3-base libgstreamer-plugins-base1.0-dev python3-opencv
sudo apt install -y git cmake make gcc

sudo apt -y install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade pip
sudo -H pip3 install boto3 dlib

cd
git clone --recursive https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp.git
mkdir -p amazon-kinesis-video-streams-producer-sdk-cpp/build
cd amazon-kinesis-video-streams-producer-sdk-cpp/build
cmake -DBUILD_GSTREAMER_PLUGIN=ON ..
make

cd
sudo apt-get update
sudo apt-get -y install git
sudo apt-get -y install autoconf cmake bison automake libtool gcc flex
sudo apt-get -y install gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools
sudo apt-get -y install gstreamer1.0-omx
sudo apt-get -y install gstreamer1.0
sudo apt-get -y install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-base-apps
sudo apt-get -y install libssl-dev libcurl4-openssl-dev liblog4cplus-1.1-9 liblog4cplus-dev glib libglib libglib2.0 libglib2.0-dev

sudo -H pip3 install boto3 dlib
sudo -H pip3 install opencv
sudo apt install libopencv-dev libcv2.4 libcvaux2.4 libcvaux-dev libhighgui-dev libhighgui2.4 libopencv-highgui-dev libopencv-highgui2.4-deb0 libopencv-imgproc2.4v5 libopencv-imgproc-dev
sudo apt install python-opencv python-numpy python-scipy python-matplotlib python-urllib3
sudo -H pip3 install opencv-python
sudo -H pip3 install --upgrade numpy
sudo -H pip3 install --upgrade numpy
sudo -H pip3 install --upgrade opencv-python
sudo pip3 list 

cat /etc/modules
echo 'bcm2835-v4l2' | sudo tee -a /etc/modules
cat /etc/modules


cd ~/surveillance-app/
#vi .env 
#up_cam.sh
#python3 main.py 


