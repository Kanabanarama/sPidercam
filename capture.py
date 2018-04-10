from picamera import PiCamera
from time import sleep

camera = PiCamera()

for i in range(10):
    camera.capture('test%s.jpg' % i)
    sleep(5)
