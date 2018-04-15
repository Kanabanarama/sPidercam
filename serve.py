from flask import Flask, render_template, send_from_directory, jsonify, Response
import os
import io
import time
import datetime
import picamera

app = Flask(__name__)

livestream = ['stream.mjpg']

def getVideos():
    #videos = [folder + '/video.mp4' for folder in os.listdir('timelapse/videos')]
    #print(videos[:])
    return os.listdir('timelapse/videos')

@app.template_filter('to_day_name')
def to_day_name_filter(s):
    weekday = datetime.datetime.strptime(s, '%Y-%m-%d').strftime('%a')
    return weekday

@app.route('/timelapse/videos/<path:path>')
def send_thumbnail(path):
    return send_from_directory('timelapse/videos', path)

@app.route('/')
def index():
    return render_template('index.html', livestream = livestream, videos = getVideos())

@app.route('/json')
def json_index():
    return jsonify('hello spider!')

@app.route('/json/livestream')
def json_livestream():
    return jsonify(livestream)

@app.route('/json/timelapse')
def json_timelapse():
    return jsonify(getVideos())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
