"""
Serve html files and media for web frontend and json for mobile app
"""

import os
import datetime
from flask import Flask, render_template, send_from_directory, jsonify, Response

import io
import time
import picamera

APP = Flask(__name__)

def get_livestream_filename():
    "Returns the stream filename"
    return ['stream.mjpg']

def frameGenerator():
    """Camera stream generator function"""
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 360)
        camera.framerate = 30
        time.sleep(1)
        stream = io.BytesIO()
        for ioBytes in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
            stream.seek(0)
            frame = stream.read()
            yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            stream.seek(0)
            stream.truncate()

def get_video_dirs():
    "Returns the folders containing timelapse videos (and their thumbnails)"
    #videos = [folder + '/video.mp4' for folder in os.listdir('timelapse/videos')]
    #print(videos[:])
    return os.listdir('timelapse/videos')

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
    return Response(frameGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)
