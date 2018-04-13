import threading
import picamera
import time

def capture_video(device):
    device.start_recording('test.mp4', format='mjpeg')
    device.wait_recording(25)
    device.stop_recording()
    print("recording finished")

def capture_image(device):
    # using the still port would cause dropped frames due to camera mode change
    device.capture('test.jpg', use_video_port=True)
    print("capture finished")

if __name__ == '__main__':
    camera = picamera.PiCamera(resolution='800x600', framerate=25)

    p1 = threading.Thread(target=capture_video, args=(camera,))
    p2 = threading.Thread(target=capture_image, args=(camera,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    camera.close()
