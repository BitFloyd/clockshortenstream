import cv2
import os
import numpy as np
from ..logging_pkg.logging import *


class Stream:

    def __init__(self, path_to_input_video, time_resolution,debug=False):
        self.path_to_input_video = path_to_input_video

        self.time_resolution = time_resolution

        self.debug = debug

        if(debug):
            self.process_debug_save_routine()

        self.get_frameReader()

    def process_debug_save_routine(self):
        debug_path = os.path.join(os.path.split(self.path_to_input_video)[0], 'debug_files')
        if (not os.path.exists(debug_path)):
            os.mkdir(debug_path)
        self.debug_path = debug_path

    def get_frameReader(self):
        self.frameReader = FrameReader(pathToVideo=self.path_to_input_video)
        timeperiod = 1/(self.frameReader.videoFPS+0.0)

        if(self.time_resolution==None):
            self.time_resolution = timeperiod
        else:
            self.time_resolution = int(self.time_resolution/timeperiod)*timeperiod

        message_print("TIME_RESOLUTION:"+str(self.time_resolution))

        self.time_in_seconds = self.frameReader.numFrames / self.frameReader.videoFPS

        self.num_read_iterations = int((self.time_in_seconds) / self.time_resolution)
        self.videoFinished = False

        return self.frameReader

    def readNextFrameFromVideo(self):
        frame = self.frameReader.getFrameAfterTSeconds(t=self.time_resolution)

        self.videoFinished = self.frameReader.videoFinished

        return frame

    def restart_Stream(self):
        self.frameReader.closeFrameReader()
        self.frameReader = self.get_frameReader()

        return self.frameReader

    def close_Stream(self):
        self.frameReader.closeFrameReader()

        return True


class FrameReader:

    def __init__(self,pathToVideo,debug_mode=False):

        self.pathToVideo = pathToVideo
        self.debug_mode = debug_mode

        self.videoContainer = cv2.VideoCapture(self.pathToVideo)
        self.videoFPS = self.videoContainer.get(cv2.CAP_PROP_FPS)

        self.numFrames = self.videoContainer.get(cv2.CAP_PROP_FRAME_COUNT)


        self.videoFrameWidth = int(self.videoContainer.get(3))
        self.videoFrameHeight = int(self.videoContainer.get(4))

        message_print("VIDEO FPS:" + str(self.videoFPS))
        message_print("NUMBER OF FRAMES IN VIDEO:" + str(self.numFrames))
        message_print("FRAME WIDTH:"+str(self.videoFrameWidth))
        message_print("FRAME HEIGHT:" + str(self.videoFrameHeight))


        self.videoFinished = False

        self.frameNumber = 0


    def readNextFrameFromVideo(self):

        self.frameNumber+=1
        ret,frame = self.videoContainer.read()


        if(not ret):
            self.videoFinished = True

        if(self.videoFinished):
            return np.array(0)

        return frame


    def getFrameAfterTSeconds(self,t=0):

        #t must be in seconds.

        next_frame = int(self.frameNumber + t*self.videoFPS)

        if(next_frame>self.numFrames):
            self.videoFinished = True
            return np.array(0)

        self.videoContainer.set(cv2.CAP_PROP_POS_FRAMES,next_frame)

        frame = self.readNextFrameFromVideo()

        self.frameNumber = next_frame

        return frame

    def getFrameAtFrameNumber(self,frame_num):

        self.videoContainer.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        frame = self.readNextFrameFromVideo()

        return frame

    def closeFrameReader(self):
        self.videoContainer.release()
        return True
