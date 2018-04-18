"""
Serve html files and media for web frontend and json for mobile app
"""

import os
import threading
import io
import time
import datetime
import picamera
import timelapse
from flask import Flask, render_template, send_from_directory, jsonify, Response

APP = Flask(__name__)
CAMERA = {}

def init_camera():
    #if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    if(not len(CAMERA)):
        camera_pi = picamera.PiCamera()
        camera_pi.resolution = (1024, 576)
        camera_pi.framerate = 30
        CAMERA['picamera'] = camera_pi
    return CAMERA

def frame_generator():
    """Camera stream generator function"""
    camera = init_camera()['picamera']
    stream = io.BytesIO()
    for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True, splitter_port=2):
        stream.seek(0)
        frame = stream.read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        stream.seek(0)
        stream.truncate()

def get_livestream_filename():
    "Returns the stream filename"
    return ['stream.mjpg']

def get_video_dirs():
    "Returns the folders containing timelapse videos (and their thumbnails)"
    #videos = [folder + '/video.mp4' for folder in os.listdir('timelapse/videos')]
    #print(videos[:])
    return os.listdir('timelapse/videos')

def get_frame_dirs():
    "Returns the folders containing timelapse frames"
    return os.listdir('timelapse/frames')

@APP.template_filter('to_day_name')
def to_day_name_filter(datestring):
    "Return the weekday from a datestring in Y-m-d form"
    weekday = datetime.datetime.strptime(datestring, '%Y-%m-%d').strftime('%a')
    return weekday

@APP.route('/timelapse/videos/<path:path>')
def send_thumbnail(path):
    "Serve video and thumbnail files"
    return send_from_directory('timelapse/videos', path)

@APP.route('/')
def index():
    "Render index template"
    return render_template('index.html',
                           livestream_filename=get_livestream_filename(),
                           video_dirs=get_video_dirs())

@APP.route('/livestream')
def livestream():
    "Send the camera livestream"
    return Response(frame_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@APP.route('/json')
def json_index():
    "Return json index"
    return jsonify('hello spider!')

@APP.route('/json/livestream')
def json_livestream():
    "Return livestream filename as json"
    return jsonify(get_livestream_filename())

@APP.route('/json/timelapse')
def json_timelapse():
    "Return timelapse video folders as json"
    return jsonify(get_video_dirs())

def merge_worker():
    """Interval check frames ready to video merging"""
    if(os.path.isdir('timelapse/frames')):
        while True:
            print('--- Watching queue for finished frame captures to merge ---')
            mergedVideo = timelapse.Timelapse().merge()
            if(mergedVideo):
                timelapse.Timelapse().create_thumbnail(mergedVideo)
            time.sleep(3600)

def capture_timelapse():
    """Capture frames for the rest of the day"""
    camera = init_camera()['picamera']
    while True:
        timelapse.Timelapse().capture(camera, 5)

if __name__ == '__main__':
    p1 = threading.Thread(target=capture_timelapse)
    p1.start()
    #p1.join()
    p2 = threading.Thread(target=merge_worker)
    p2.start()
    #p2.join()
    APP.run(host='0.0.0.0', port=5000, debug=False)
