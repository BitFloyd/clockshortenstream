import cv2
import os
import numpy as np
from ..logging_pkg.logging import *

class FrameWriter:
    def __init__(self, save_path, video_name, frame_size=(10, 10),video_fps=12):

        self.pathToShots = save_path
        self.video_name = video_name
        self.frame_size = frame_size
        self.frame_count = 0
        self.video_fps = video_fps


    def openVideoStream(self):
        shotFileName = os.path.join(self.pathToShots, self.video_name)
        message_print("OUTPUT_FILE_PATH: "+shotFileName)
        self.videoWriter = cv2.VideoWriter(shotFileName, cv2.VideoWriter_fourcc('F', 'M', 'P', '4'),
                                           self.video_fps, (self.frame_size[1], self.frame_size[0]))

        return True

    def writeFrameToVideo(self, frame):
        self.videoWriter.write(frame)
        self.frame_count += 1

        return True

    def closeVideoStream(self):
        self.videoWriter.release()

        return True