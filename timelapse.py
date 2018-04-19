"""
Make timelapse videos
"""

import os
import re
import datetime
import collections
import time
import ffmpy

class Timelapse:
    """
    Daily start (and continue) image capturing to merge them into videos
    """
    frame_path = 'timelapse/frames'
    video_path = 'timelapse/videos'
    merge_queue = collections.OrderedDict()

    def set_frame_path(self, path):
        """Sets the path where frame images are stored"""
        self.frame_path = path

    def set_video_path(self, path):
        """Sets the path where merged videos are saved to"""
        self.video_path = path

    @classmethod
    def get_highest_frame_number(cls, frame_dir):
        """Get the last captured frame number in a frame dir"""
        list_of_files = os.listdir(frame_dir)
        max_framenum = 1
        for filename in list_of_files:
            current_framenum = int(re.search(r'\d+', filename).group(0))
            max_framenum = max(current_framenum, max_framenum)
        return max_framenum + 1

    def capture(self, device, interval):
        """Begin capture images from a camera with an interval"""
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        remaining_seconds = (midnight - now).seconds
        remaining_shots = round(remaining_seconds / interval)
        dir_name = now.strftime("%Y-%m-%d")
        output_path = self.frame_path + '/' + dir_name
        os.makedirs(output_path, exist_ok=True)

        print("--- Capturing %i images in intervals of %i seconds ---"
              % (remaining_shots, interval))

        latest_frame_num = self.get_highest_frame_number(output_path)
        print("--- Beginning from file with number %i ---" % latest_frame_num)

        for i in range(remaining_shots):
            frame_num = latest_frame_num + i
            frame_file = "frame%i.jpg" % frame_num
            # using the still port would cause dropped frames due to
            # camera mode change
            device.capture('%s/%s' % (output_path, frame_file),
                           use_video_port=True, splitter_port=1)
            print("> captured %s (remaining: %i)" % (frame_file, remaining_shots - i + 1))
            time.sleep(interval)

        print('--- Finished frame capturing for [%s], put into queue for merging' % output_path)
        self.merge_queue[output_path] = self.video_path + '/' + dir_name

    @classmethod
    def rebuild_merge_queue(cls):
        """Fill queue with frame sets that were not yet merged to a video"""
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_date = time.strptime(today.strftime('%Y-%m-%d'), "%Y-%m-%d")

        list_of_timelapse_folders = os.listdir(cls.frame_path)
        for folder in list_of_timelapse_folders:
            folder_date = time.strptime(folder, "%Y-%m-%d")
            if folder_date < today_date:
                past_frames_path = cls.frame_path + '/' + folder
                past_video_path = cls.video_path + '/' + folder
                if not os.path.isfile(past_video_path+'/video.mp4'):
                    print('--- Found past unconverted timelapse frames in [%s]'
                          ', added to queue' % past_frames_path)
                    cls.merge_queue[past_frames_path] = past_video_path

    @classmethod
    def merge(cls):
        """Starts merging the next frames in the queue"""
        result = None
        if cls.merge_queue:
            next_element = cls.merge_queue.popitem()
            print('--- Merge next queue item: %s ---' % next_element[0])
            frame_path = next_element[0]
            output_path = next_element[1]

            os.makedirs(output_path, exist_ok=True)
            ff_command = ffmpy.FFmpeg(
                inputs={'%s/frame%%01d.jpg' % frame_path: '-f image2 -r 30/1'},
                outputs={'%s/video.mp4' % output_path:
                         '-y -vcodec libx264 -pix_fmt yuv420p -crf 18 '
                         '-preset medium'} #veryslow
            )
            ff_command.run()
            # as command:
            #os.system("ffmpeg -f image2 -r 30/1 -i %s/frame%%01d.png
            #-vcodec mpeg4 -y %s/video.mp4" % (framePath, timelapsePath))
            result = '%s/video.mp4' % output_path
        return result

    @classmethod
    def create_thumbnail(cls, video_path):
        """Make a thumbnail of a video"""
        ff_command = ffmpy.FFmpeg(
            inputs={'%s/video.mp4' % video_path: None},
            outputs={'%s/thumbnail.jpg' % video_path: '-ss 0:0:00 -vframes 1 -q:v 2'}
        )
        ff_command.run()
        # as command:
        #os.system("ffmpeg -i video.mp4 -ss 00:00:00 -vframes 1 -q:v 2 screenshot.jpg")
        return '%s/thumbnail.jpg' % video_path
