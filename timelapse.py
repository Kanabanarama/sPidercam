import os
import ffmpy
from time import sleep

class Timelapse:
    def capture(self, device, shots, interval, outputPath):
        if(os.path.isdir(outputPath)):
            for i in os.listdir(outputPath):
                os.remove(os.path.join(outputPath, i))
            os.rmdir(outputPath)
            print("removed existing directory [%s]" % outputPath)

        os.makedirs(outputPath)

        print("capturing %i images in intervals of %i seconds"
            % (shots, interval)
        )

        for i in range(shots):
            frameNum = i + 1
            frameFile = "frame%i.jpg" % frameNum
            # using the still port would cause dropped frames due to camera mode change
            device.capture('%s/%s' % (outputPath, frameFile), use_video_port=True)
            print("> captured %s (remaining: %i)" % (frameFile, shots - frameNum))
            sleep(interval)

    def merge(self, framePath, outputPath):
        timelapseFile = "video.mp4"

        os.makedirs(outputPath, exist_ok=True)

        ff = ffmpy.FFmpeg(
             inputs={'%s/frame%%01d.jpg' % framePath: '-f image2 -r 30/1'},
             outputs={'%s/video.mp4' % outputPath: '-y -vcodec libx264 -crf 18 -preset veryslow'}
        )
        ff.run()

        # as command:
        #os.system("ffmpeg -f image2 -r 30/1 -i %s/frame%%01d.png -vcodec mpeg4 -y %s/video.mp4" % (framePath, timelapsePath))
