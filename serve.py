"""
Serve html files and media for web frontend and json for mobile app
"""

import os
import threading
import io
import time
import datetime
import picamera
import flask
import timelapse

APP = flask.Flask(__name__)
CAMERA = {}

def init_camera():
    """Retrieve picamera object"""
    #if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    if not CAMERA:
        camera_pi = picamera.PiCamera()
        camera_pi.resolution = (1024, 576)
        camera_pi.framerate = 30
        camera_pi.rotation = 90
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

@APP.route('/timelapse/videos/<path:path>/thumbnail.jpg')
def send_thumbnail(path):
    "Serve thumbnail files"
    return flask.send_from_directory('timelapse/videos/%s' %path, 'thumbnail.jpg')

@APP.route('/timelapse/videos/<path:path>/video.mp4')
def stream_video(path):
    "Stream mp4 timelapse videos"
    fp_as_string = 'timelapse/videos/%s/video.mp4' % path
    video = open(fp_as_string, 'rb')
    def read_chunks(file_object, chunk_size=1024):
        "Read a file in chunks"
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data
    return flask.Response(
        flask.stream_with_context(read_chunks(video)),
        mimetype='video/mp4')

@APP.route('/')
def index():
    "Render index template"
    return flask.render_template('index.html',
                                 livestream_filename=get_livestream_filename(),
                                 video_dirs=get_video_dirs())

@APP.route('/livestream')
def livestream():
    "Send the camera livestream"
    return flask.Response(frame_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@APP.route('/json')
def json_index():
    "Return json index"
    return flask.jsonify('hello spider!')

@APP.route('/json/livestream')
def json_livestream():
    "Return livestream filename as json"
    return flask.jsonify(get_livestream_filename())

@APP.route('/json/timelapse')
def json_timelapse():
    "Return timelapse video folders as json"
    return flask.jsonify(get_video_dirs())

def merge_worker():
    """Interval check frames ready to video merging"""
    if os.path.isdir('timelapse/frames'):
        timelapse.Timelapse.rebuild_merge_queue()
        while True:
            merged_video = timelapse.Timelapse.merge()
            if merged_video:
                timelapse.Timelapse.create_thumbnail(merged_video)
            time.sleep(3600)

def capture_timelapse():
    """Capture frames for the rest of the day"""
    camera = init_camera()['picamera']
    while True:
        timelapse.Timelapse().capture(camera, 5)

if __name__ == '__main__':
    #TIMELAPSE_THREAD = threading.Thread(target=capture_timelapse)
    #TIMELAPSE_THREAD.start()
    #TIMELAPSE_THREAD.join()
    MERGE_THREAD = threading.Thread(target=merge_worker)
    MERGE_THREAD.start()
    #MERGE_THREAD.join()
    APP.run(host='0.0.0.0', port=5000, debug=False)
