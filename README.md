# sPidercam

Raspberry Pi camera playground

### HARDWARE:

- Raspberry Pi (A+ or similar)
- Pi or Pi Noir camera
- SD/MicroSD card
- optional: Raspberry Pi case with camera mount
- optional: magnetic smartphone macro/fisheye lens

### INSTALLATION

#### Install OS

Put an suitable OS on your raspberry pi's SD card, for example raspian lite:

https://www.raspberrypi.org/downloads/raspbian

Installation guide:

https://www.raspberrypi.org/documentation/installation/installing-images/README.md

#### Enable the camera

Configuration guide:

https://www.raspberrypi.org/documentation/configuration/camera.md

#### Test the camera

```
raspistill -v -o test.jpg
```

It should save an image with the filename test.jpg in the raspberry pi's home folder.

#### Install python packages
```
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
```

#### Install ffmpeg

```
cd /usr/src
sudo mkdir ffmpeg
sudo chown pi:users ffmpeg
git clone git://source.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg
./configure
make && sudo make install
```

(Takes pretty long)

#### Install picamera and python wrapper for ffmpeg
```
pip3 install picamera
pip3 install ffmpy
```

### USAGE

```
python3 timelapse.py
```
