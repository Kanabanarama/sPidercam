import os
import re
import ffmpy
import collections
from time import sleep, time

class Timelapse:
    frame_path = 'timelapse/frames'
    video_path = 'timelapse/videos'
    merge_queue = collections.OrderedDict()

    def set_frame_path(self, path):
        self.frame_path = path

    def set_video_path(self, path):
        self.video_path = path

    def get_highest_frame_number(self, frame_dir):
        list_of_files = os.listdir(frame_dir)
        max_framenum = 1
        for filename in list_of_files:
            current_framenum = int(re.search('\d+', filename).group(0))
            max_framenum = max(current_framenum, max_framenum)
        return max_framenum + 1

    def capture(self, device, shots, interval, dirName):
        outputPath = self.frame_path + '/' + dirName
        os.makedirs(outputPath, exist_ok=True)

        print("--- Capturing %i images in intervals of %i seconds ---"
            % (shots, interval)
        )

        latestFrameNum = self.get_highest_frame_number(outputPath)
        print("--- Beginning from file with number %i ---" % latestFrameNum)

        for i in range(shots):
            frameNum = latestFrameNum + i
            frameFile = "frame%i.jpg" % frameNum
            # using the still port would cause dropped frames due to camera mode change
            device.capture('%s/%s' % (outputPath, frameFile), use_video_port=True, splitter_port=1)
            print("> captured %s (remaining: %i)" % (frameFile, shots - i + 1))
            sleep(interval)

        print('--- Finished frame capturing for [%s], put into queue for merging' % outputPath)
        self.merge_queue[outputPath] = self.video_path + '/' + dirName

    #@staticmethod
    def merge(self, inputFramePath=None, outputVideoPath=None): #inputFramePath, outputVideoPath):
        if(len(self.merge_queue)):
            nextElement = self.merge_queue.popitem()
            print('--- Merge next queue item: %s ---' % nextElement)
            framePath = nextElement[0]
            outputPath = nextElement[1]

            os.makedirs(outputPath, exist_ok=True)
            ff = ffmpy.FFmpeg(
                 inputs={'%s/frame%%01d.jpg' % framePath: '-f image2 -r 30/1'},
                 outputs={'%s/video.mp4' % outputPath: '-y -vcodec libx264 -pix_fmt yuv420p -crf 18 -preset medium'} #veryslow
            )
            ff.run()
            # as command:
            #os.system("ffmpeg -f image2 -r 30/1 -i %s/frame%%01d.png -vcodec mpeg4 -y %s/video.mp4" % (framePath, timelapsePath))
            return '%s/video.mp4' % outputPath

    #@staticmethod
    def create_thumbnail(videoPath):
        ff = ffmpy.FFmpeg(
             inputs={'%s/video.mp4' % videoPath: None},
             outputs={'%s/thumbnail.jpg' % outputPath: '-ss 0:0:00 -vframes 1 -q:v 2'}
        )
        ff.run()
        # as command:
        #os.system("ffmpeg -i video.mp4 -ss 00:00:00 -vframes 1 -q:v 2 screenshot.jpg")
        return '%s/thumbnail.jpg' % outputPath
