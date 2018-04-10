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

#### Install packages
```
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-picamera
```

#### Clone repository
```
git clone https://github.com/Kanabanarama/sPidercam
```

### USAGE

```
python3 capture.py
```