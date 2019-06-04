import os
from frame_reader import Stream
from ..functionals_pkg.plot_functions import plot_histogram
from skimage.io import imsave
from frame_writer import FrameWriter, WriteTimeIntervalsToNewVideo
from tqdm import tqdm
from ..process_frame_pkg.framepy import *
import cv2
import numpy as np
from ..logging_pkg.logging import *
from ..functionals_pkg.save_objects import *
from skimage.measure import compare_ssim
from commercial_break_remover import CommercialRemoverBasic


class GetBoxesInStream:

    def __init__(self,stream,debug=False):
        self.path_to_input_video = stream.path_to_input_video
        self.time_resolution = stream.time_resolution
        self.stream = stream
        self.debug = debug

    def get_boxes(self):

        self.stream.restart_Stream()
        progress_bar = tqdm(total=self.stream.num_read_iterations)
        frame = self.stream.readNextFrameFromVideo()

        cropped_frame = crop_image_to_percent(img=frame,axis='y',part_image='top',percentage=0.25)
        mean_box_image = np.zeros((cropped_frame.shape[0],cropped_frame.shape[1]))


        i = 0
        while not self.stream.videoFinished:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            frame = crop_image_to_percent(img=frame,axis='y',part_image='top',percentage=0.25)
            if(self.debug):
                imsave(fname=os.path.join(self.stream.debug_path,str(i)+'_agrey_frame.png'),arr=frame)

            frame = canny_edge(img=frame)
            if(self.debug):
                imsave(fname=os.path.join(self.stream.debug_path,str(i)+'_bcanny_edge_frame.png'),arr=frame)


            frame = get_boxes_in_image(frame)
            if (self.debug):
                imsave(fname=os.path.join(self.stream.debug_path, str(i) + '_dboxes_frame.png'), arr=frame)

            mean_box_image = (mean_box_image * i + frame) / (i + 1)
            i+=1

            frame = self.stream.readNextFrameFromVideo()

            progress_bar.update(1)

        progress_bar.close()


        mean_box_image = np.uint8(mean_box_image)
        if (self.debug):
            imsave(fname=os.path.join(self.stream.debug_path,'mean_boxes_frame_wo_threshold.png'), arr=frame)

        mean_box_image = binary_threshold(mean_box_image)

        x_stats = get_vertical_line_stats_in_x_axis(mean_box_image)
        y_stats = get_horizontal_line_stats_in_y_axis(mean_box_image)
        stats = (x_stats, y_stats)

        self.stats = stats
        self.mean_box_image = mean_box_image

        return stats,mean_box_image

    def saveGetBoxesInStream(self):
        save_obj(self, 'GetBoxesInStream.pkl')

class GetXYLimitsOfBoxes:

    def __init__(self,stats,x_threshold,y_threshold):

        self.x_threshold = x_threshold
        self.y_threshold = y_threshold

        self.x_stats = stats[0]
        self.y_stats = stats[1]



    def get_limits_stats(self):

        x_stats = self.x_stats[0] / np.max(self.x_stats[0])

        x_stats = (x_stats * (x_stats > self.x_threshold)).tolist()
        x_stats_limits = [n for n, i in enumerate(x_stats) if i > 0]
        x_limits = (x_stats_limits[0], x_stats_limits[-1])
        print ('x_limits:', x_limits)

        y_stats = self.y_stats.transpose()[0] / np.max(self.y_stats.transpose()[0])

        y_stats = (y_stats * (y_stats > self.y_threshold)).tolist()
        y_stats_limits = [n for n, i in enumerate(y_stats) if i > 0]
        y_limits = (y_stats_limits[0], y_stats_limits[-1])
        print ('y_limits:', y_limits)

        self.limits = (x_limits,y_limits)

        self.filtered_x_stats = x_stats
        self.filtered_y_stats = y_stats

        filtered_stats = (self.filtered_x_stats,self.filtered_y_stats)


        return self.limits, filtered_stats

    def saveLimits(self):
        save_obj(self.limits,'Limits.pkl')
        return True

    def loadLimits(self):
        self.limits = load_obj('Limits.pkl')

    def saveFilteredStats(self):
        filtered_stats = (self.filtered_x_stats, self.filtered_y_stats)
        save_obj(filtered_stats,'FilteredStats.pkl')

        return True

    def loadFilteredStats(self):

        filtered_stats = load_obj('FilteredStats.pkl')
        self.filtered_x_stats = filtered_stats[0]
        self.filtered_y_stats = filtered_stats[1]

        return True

    def saveGetXYLimitsOfBoxes(self):
        save_obj(self,'GetXYLimitsOfBoxes.pkl')

class GetMeanOfWindow:

    def __init__(self,stream,limits):
        self.stream = stream
        self.x_limits = limits[0]
        self.y_limits = limits[1]
        self.time_resolution = self.stream.time_resolution


    def get_mean_of_window(self):

        self.stream.restart_Stream()
        progress_bar = tqdm(total=self.stream.num_read_iterations)
        frame = self.stream.readNextFrameFromVideo()

        window = crop_window_from_image(frame, x_limits=self.x_limits, y_limits=self.y_limits)
        mean_window_image = np.zeros(window.shape)

        i = 0

        while not self.stream.videoFinished:

            window = crop_window_from_image(frame, x_limits=self.x_limits, y_limits=self.y_limits)
            mean_window_image = (mean_window_image * i + window) / (i + 1)
            i+=1

            frame = self.stream.readNextFrameFromVideo()


            progress_bar.update(1)

        progress_bar.close()


        mean_window_image = np.uint8(mean_window_image)

        self.mean_window_image = mean_window_image

        return mean_window_image

    def saveGetMeanOfWindow(self):
        save_obj(self, 'GetMeanOfWindow.pkl')

class GetSimilarityOfWindow:

    def __init__(self,stream,limits,window_mean):
        self.stream = stream
        self.x_limits = limits[0]
        self.y_limits = limits[1]
        self.window_mean = window_mean
        self.ssimstats = []

    def get_ssim_stats_of_window_from_stream(self):

        self.stream.restart_Stream()
        progress_bar = tqdm(total=self.stream.num_read_iterations)
        frame = self.stream.readNextFrameFromVideo()


        while not self.stream.videoFinished:

            ssim_measure = self.get_ssim_of_frame(frame)

            frame = self.stream.readNextFrameFromVideo()

            self.ssimstats.append(ssim_measure)

            progress_bar.update(1)

        progress_bar.close()

        return np.array(self.ssimstats)

    def saveGetSimilarityOfWindow(self):
        save_obj(self, 'GetSimilarityOfWindow.pkl')

    def get_ssim_of_frame(self,frame):
        window = crop_window_from_image(frame, x_limits=self.x_limits, y_limits=self.y_limits)
        ssim_measure = compare_ssim(X=self.window_mean, Y=window, multichannel=True,
                                    win_size=9)

        return ssim_measure

class FramesWithClockPresent:

    def __init__(self,stream,limits,ssim_threshold=0.6):
        self.path_to_input_video = stream.path_to_input_video
        self.time_resolution = stream.time_resolution
        self.stream = stream

        self.x_limits = limits[0]
        self.y_limits = limits[1]


        self.list_ssim_measure = []
        self.list_clock_present = []

        self.ssim_threshold = ssim_threshold

    def prepareListOfFramesWithClockPresenceSSIM(self,window_mean):

        self.stream.restart_Stream()
        progress_bar = tqdm(total=self.stream.num_read_iterations)
        frame = self.stream.readNextFrameFromVideo()

        while not self.stream.videoFinished:

            window = crop_window_from_image(frame, x_limits=self.x_limits, y_limits=self.y_limits)
            ssim_measure = compare_ssim(X=window_mean,Y=window,multichannel=True,
                                        win_size=min([window.shape[0],window.shape[1]])/5)

            frame = self.stream.readNextFrameFromVideo()

            self.list_ssim_measure.append(ssim_measure)
            self.list_clock_present.append(np.round(ssim_measure,decimals=1)>=self.ssim_threshold)

            progress_bar.update(1)

        progress_bar.close()

        return True

    def saveFramesWithClockPresent(self):
        save_obj(self,'FramesWithClockPresent.pkl')

class WriteStreamWithDetectedClock:

    def __init__(self,frameswithclockpresent,path_to_save_output_video,debug=False):

        self.path_to_save_output_video = path_to_save_output_video
        self.clockpresence = frameswithclockpresent
        self.path_to_input_video = self.clockpresence.stream.path_to_input_video
        self.stream = self.clockpresence.stream
        self.debug = debug
        self.x_limits = self.clockpresence.x_limits
        self.y_limits = self.clockpresence.y_limits


        self.frameReader = self.stream.restart_Stream()

    def getFrameWriter(self,frame_shape,write_fps):

        self.frameWriter = FrameWriter(save_path=self.path_to_save_output_video,
                                  video_name='stream_with_detected_clock.mp4',
                                  frame_size=frame_shape,video_fps=write_fps)

        return self.frameWriter

    def processFrame(self,frame,index):

        if (self.clockpresence.list_clock_present[index]):
            frame = draw_rectangle_on_image(frame, x_limits=self.x_limits, y_limits=self.y_limits)


        frame = cv2.putText(frame, text=str(self.clockpresence.list_ssim_measure[index]),
                            org=(150, 60),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1,
                            color=(255, 0, 0),
                            thickness=2, lineType=2)

        if(self.debug):
            imsave(fname=os.path.join(self.stream.debug_path,str(index)+'_processedFrameforWriting.png'),arr=frame)


        self.frameWriter.writeFrameToVideo(frame)

        return True

    def writeStreamWithDetectedClock(self,write_fps=12):

        self.stream.restart_Stream()
        frame = self.stream.readNextFrameFromVideo()

        frameWriter = self.getFrameWriter(frame_shape=frame.shape,write_fps=write_fps)

        pbar = tqdm(total=self.stream.num_read_iterations)

        i = 0
        frameWriter.openVideoStream()

        while not self.stream.videoFinished:

            self.processFrame(frame,i)

            frame = self.stream.readNextFrameFromVideo()

            pbar.update(1)
            i += 1

        pbar.close()

        frameWriter.closeVideoStream()

class GetTimeIntervalsWithClocks:

    def __init__(self, stream, similarity_obj, ssim_threshold=0.6):
        self.stream = stream
        self.list_clock_present_per_frame = []
        self.list_clock_present_time = []
        self.list_time_intervals = []

        self.similarity_obj = similarity_obj
        self.ssim_threshold = ssim_threshold

        self.time_resolution = self.stream.time_resolution
        self.max_clock_disappear_allowance_time = 15

    def create_frame_time_lists(self):

        self.stream.restart_Stream()
        self.time_resolution = self.stream.time_resolution

        i = 1
        progress_bar = tqdm(total=self.stream.num_read_iterations)
        frame = self.stream.readNextFrameFromVideo()

        while not self.stream.videoFinished:

            ssim_measure = self.similarity_obj.get_ssim_of_frame(frame)
            self.list_clock_present_per_frame.append(ssim_measure > self.ssim_threshold)
            self.list_clock_present_time.append(i * self.time_resolution)
            i += 1
            frame = self.stream.readNextFrameFromVideo()
            progress_bar.update(1)

        progress_bar.close()

        return True

    def process_frame_time_lists_to_time_intervals(self):

        self.list_time_intervals = []

        idx_clock_present = 0

        look_ahead = self.max_clock_disappear_allowance_time / (self.time_resolution + 0.0)

        while idx_clock_present < len(self.list_clock_present_per_frame):

            while (not self.list_clock_present_per_frame[idx_clock_present]):
                idx_clock_present += 1

                if(idx_clock_present >= len(self.list_clock_present_per_frame)):
                    break
            if (idx_clock_present >= len(self.list_clock_present_per_frame)):
                break

            clock_presence_ratio = sum(self.list_clock_present_per_frame[idx_clock_present:idx_clock_present + int(look_ahead)]) / look_ahead

            if (clock_presence_ratio > 0.25):
                time_interval_start = self.list_clock_present_time[idx_clock_present]
            else:
                idx_clock_present += 1
                continue

            end_flag = False
            while (not end_flag):
                end_clock_sum = sum(self.list_clock_present_per_frame[idx_clock_present:idx_clock_present + int(look_ahead)])
                end_clock_detection_ratio = end_clock_sum / look_ahead

                if (end_clock_detection_ratio < 0.1):
                    end_flag = True

                idx_clock_present += 1

            time_interval_end = self.list_clock_present_time[idx_clock_present - 1]

            time_interval = (time_interval_start, time_interval_end)

            self.list_time_intervals.append(time_interval)

            self.look_ahead_int = int(look_ahead)

        return self.list_time_intervals

    def saveGetTimeIntervalsWithClocks(self):
        save_obj(self, 'GetTimeIntervalsWithClocks.pkl')

class WriteTimeIntervalsToVideo:

    def __init__(self,stream,time_intervals,path_to_output_video,path_to_output_srt,path_to_input_video,path_to_input_srt):
        self.stream = stream
        self.time_intervals = time_intervals
        self.path_to_output_video = path_to_output_video
        self.path_to_output_srt = path_to_output_srt
        self.path_to_input_video = path_to_input_video
        self.path_to_input_srt = path_to_input_srt

    def concatenate_clips(self):
        writeTimeIntervals = WriteTimeIntervalsToNewVideo(self.time_intervals, self.path_to_input_video,
                                                          self.path_to_input_srt, self.path_to_output_video,
                                                          self.path_to_output_srt)
        writeTimeIntervals.concatenate_clips()

    def write_time_intervals_to_video(self):

        self.concatenate_clips()

        return True

class DetectClockInVideo:

    def __init__(self,path_to_input_video,path_to_save_output_video):
        self.path_to_input_video = path_to_input_video
        self.path_to_save_output_video = path_to_save_output_video


    def detect_clock(self):

        stream = Stream(path_to_input_video=self.path_to_input_video, time_resolution=1)
        getBoxes = GetBoxesInStream(stream)
        stats, mean_box_image = getBoxes.get_boxes()
        cv2.imwrite(filename='mean_box_image.png', img=mean_box_image)

        getLimits = GetXYLimitsOfBoxes(stats=stats, x_threshold=0.35, y_threshold=0.35)
        limits, filtered_stats = getLimits.get_limits_stats()


        getMeanOfWindow = GetMeanOfWindow(stream=stream, limits=limits)
        meanWindowImage = getMeanOfWindow.get_mean_of_window()
        cv2.imwrite(filename='mean_box_interior_image.png', img=meanWindowImage)


        getSSIM = GetSimilarityOfWindow(stream=stream, limits=limits, window_mean=meanWindowImage)
        ssim_stats_array = getSSIM.get_ssim_stats_of_window_from_stream()
        plot_histogram(filename='ssim_hist.png', metric_name='SSIM of Clock Box and Frames', array=ssim_stats_array)



        clockPresence = FramesWithClockPresent(stream=stream, limits=limits)
        clockPresence.prepareListOfFramesWithClockPresenceSSIM(window_mean=meanWindowImage)

        writeStream = WriteStreamWithDetectedClock(frameswithclockpresent=clockPresence,
                                                   path_to_save_output_video=self.path_to_save_output_video, debug=False)

        writeStream.writeStreamWithDetectedClock(write_fps=5)


        return True


class ShortenVideoStream:

    def __init__(self, path_to_input_video, path_to_input_srt, commercial_removed=True):

        self.path_to_input_video = path_to_input_video
        self.path_to_input_srt = path_to_input_srt


        self.commercial_removed = commercial_removed

        if(not self.commercial_removed):
            filename,ext = os.path.splitext(self.path_to_input_video)
            self.com_removed_video_path = filename+'com_removed.mp4'
            self.com_removed_srt_path = filename+'com_removed.srt'

    def remove_commercial_from_video(self):
        commercialRemover = CommercialRemoverBasic(path_to_input_video=self.path_to_input_video,
                                                   path_to_input_srt=self.path_to_input_srt,
                                                   path_to_output_video=self.com_removed_video_path,
                                                   path_to_output_srt=self.com_removed_srt_path)
        commercialRemover.remove_frames_with_commercial_break_in_progress()

        return self.com_removed_video_path, self.com_removed_srt_path

    def shorten_video_stream(self, path_to_output_video, path_to_output_srt):

        if(not self.commercial_removed):
            self.com_removed_video_path, self.com_removed_srt_path = self.remove_commercial_from_video()
        else:
            self.com_removed_video_path, self.com_removed_srt_path= self.path_to_input_video, self.path_to_input_srt

        stream = Stream(path_to_input_video=self.com_removed_video_path, time_resolution=1)
        getBoxes = GetBoxesInStream(stream)
        stats, mean_box_image = getBoxes.get_boxes()
        cv2.imwrite(filename='mean_box_image.png', img=mean_box_image)

        getLimits = GetXYLimitsOfBoxes(stats=stats, x_threshold=0.35, y_threshold=0.5)
        limits, filtered_stats = getLimits.get_limits_stats()


        getMeanOfWindow = GetMeanOfWindow(stream=stream, limits=limits)
        meanWindowImage = getMeanOfWindow.get_mean_of_window()
        cv2.imwrite(filename='mean_box_interior_image.png', img=meanWindowImage)


        getSSIM = GetSimilarityOfWindow(stream=stream, limits=limits, window_mean=meanWindowImage)
        ssim_stats_array = getSSIM.get_ssim_stats_of_window_from_stream()
        plot_histogram(filename='ssim_hist.png', metric_name='SSIM of Clock Box and Frames', array=ssim_stats_array)

        getTimeIntervals = GetTimeIntervalsWithClocks(stream=stream, similarity_obj=getSSIM, ssim_threshold=0.5)
        getTimeIntervals.create_frame_time_lists()
        list_time_intervals = getTimeIntervals.process_frame_time_lists_to_time_intervals()


        writetimeintervals = WriteTimeIntervalsToVideo(stream=stream,
                                                       time_intervals=getTimeIntervals.list_time_intervals,
                                                       path_to_output_video=path_to_output_video,
                                                       path_to_output_srt=path_to_output_srt,
                                                       path_to_input_video=self.com_removed_video_path,
                                                       path_to_input_srt=self.com_removed_srt_path)

        writetimeintervals.write_time_intervals_to_video()

        return path_to_output_video