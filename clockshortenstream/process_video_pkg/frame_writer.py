import cv2
import os
from subtitle_processes import SubtitleManager, concatenate_subtitles,write_to_subtitle_file
from moviepy.editor import VideoFileClip, concatenate_videoclips
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


class WriteTimeIntervalsToNewVideo:

    def __init__(self,time_intervals,path_to_input_video, path_to_input_srt, path_to_output_video, path_to_output_srt):

        self.time_intervals = time_intervals
        self.path_to_input_video = path_to_input_video
        self.path_to_input_srt = path_to_input_srt
        self.path_to_output_video = path_to_output_video
        self.path_to_output_srt = path_to_output_srt

    def concatenate_clips(self):
        list_of_clips = []
        list_of_subs = []

        for times in self.time_intervals:
            time_of_all_clips_before = 0
            for clip in list_of_clips:
                time_of_all_clips_before += clip.duration

            list_of_clips.append(VideoFileClip(self.path_to_input_video).subclip(times[0], times[1]))
            list_of_subs.append(SubtitleManager(self.path_to_input_srt).subclip(times[0], times[1], time_of_all_clips_before))

        final_clip = concatenate_videoclips(list_of_clips)
        final_srt = concatenate_subtitles(list_of_subs)

        final_clip.write_videofile(self.path_to_output_video)
        write_to_subtitle_file(final_srt, self.path_to_output_srt)