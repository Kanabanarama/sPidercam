from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Test data
videos = [
    '2018-04-07',
    '2018-04-08',
    '2018-04-09',
    '2018-04-10',
    '2018-04-11',
    '2018-04-12',
    '2018-04-13'
]

livestream = ['stream.mjpg']

@app.route('/')
def index():
    return render_template('index.html', livestream = livestream, videos = videos)

@app.route('/json')
def json_index():
    return jsonify('hello spider!')

@app.route('/json/livestream')
def json_livestream():
    return jsonify(livestream)

@app.route('/json/timelapse')
def json_timelapse():
    return jsonify(videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
