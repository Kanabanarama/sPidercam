import os
import ffmpy
from time import sleep
from datetime import datetime
from picamera import PiCamera

class Timelapse:
    def capture(self, shots, interval, outputPath):
        if(os.path.isdir(outputPath)):
            for i in os.listdir(outputPath):
                os.remove(os.path.join(outputPath, i))
            os.rmdir(outputPath)
            print("removed existing directory [%s]" % outputPath)

        os.makedirs(outputPath)

        print("capturing %i images in intervals of %i seconds"
            % (shots, interval)
        )

        camera = PiCamera()
        for i in range(shots):
            frameNum = i + 1
            frameFile = "frame%i.png" % frameNum
            camera.capture('%s/%s' % (outputPath, frameFile))
            print("> captured %s (remaining: %i)" % (frameFile, shots - frameNum))
            sleep(interval)

    def merge(self, framePath, outputPath):
        timelapseFile = "video.mp4"

        os.makedirs(outputPath, exist_ok=True)

        ff = ffmpy.FFmpeg(
             inputs={'%s/frame%%01d.png' % framePath: '-f image2 -r 30/1'},
             outputs={'%s/video.mp4' % outputPath: '-y -vcodec libx264 -crf 18 -preset veryslow'}
        )
        ff.run()

        # as command:
        #os.system("ffmpeg -f image2 -r 30/1 -i %s/frame%%01d.png -vcodec mpeg4 -y %s/video.mp4" % (framePath, timelapsePath))

timelapse = Timelapse()

intervalBetweenShots = 5
now = datetime.now()
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
remainingSeconds = (midnight - now).seconds
remainingShots = round(remainingSeconds / intervalBetweenShots)
imagesPath = "timelapse/frames/%s" % now.strftime("%Y-%m-%d")
videoPath = "timelapse/videos/%s" % now.strftime("%Y-%m-%d")

# capture frames for the rest of the day
timelapse.capture(
    shots = remainingShots,
    interval = intervalBetweenShots,
    outputPath = imagesPath
)

# merge frames into a video
timelapse.merge(framePath = imagesPath, outputPath = videoPath)
