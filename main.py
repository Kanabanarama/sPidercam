import os
import io
import picamera
import logging
import socketserver
from threading import Condition, Thread
from http import server
from datetime import datetime
from time import sleep

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    page = """\
    <html>
    <head>
    <title>picamera stream</title>
    </head>
    <body>
    <img src="stream.mjpg" />
    </body>
    </html>
    """

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = self.page.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:

        server = StreamingServer(('0.0.0.0', 8080), StreamingHandler)
        server_thread = Thread(target=server.serve_forever)
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')

        # capture frames for the rest of the day
        intervalBetweenShots = 1
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        remainingSeconds = (midnight - now).seconds
        remainingShots = round(remainingSeconds / intervalBetweenShots)
        imagesPath = "timelapse/frames/%s" % now.strftime("%Y-%m-%d")

        if(os.path.isdir(imagesPath)):
            for i in os.listdir(imagesPath):
                os.remove(os.path.join(imagesPath, i))
            os.rmdir(imagesPath)
            print("removed existing directory [%s]" % imagesPath)

        os.makedirs(imagesPath)

        # TODO: investigate why capturing images stalls the timelapse thread
        #timelapse = Timelapse()
        #timelapse_thread = Thread(target=timelapse.capture, args=(camera,
        #    remainingShots, intervalBetweenShots, imagesPath))

        try:
            server_thread.start()
            #timelapse_thread.start()
            #server_thread.join()
            #timelapse_thread.join()
            print("capturing %i images in intervals of %i seconds"
                % (remainingShots, intervalBetweenShots)
            )
            for i in range(remainingShots):
                sleep(1)
                frameNum = i + 1
                frameFile = "frame%i.jpg" % frameNum
                print("> capture %s (remaining: %i)" % (frameFile, remainingShots - frameNum))
                camera.capture('%s/%s' % (imagesPath, frameFile), use_video_port=True)
        finally :
            #camera.stop_recording(splitter_port=2)
            #camera.stop_recording(splitter_port=1)
            camera.stop_recording()
