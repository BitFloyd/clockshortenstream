import inspect

from moviepy.editor import VideoFileClip, concatenate_videoclips
from skimage.measure import compare_ssim
from tqdm import tqdm

from subtitle_processes import SubtitleManager, concatenate_subtitles, SubtitlesClip
from frame_reader import Stream
from frame_writer import *
from ..process_frame_pkg.framepy import *


class CommercialRemoverBasic:

    def __init__(self, path_to_input_video, path_to_input_srt, path_to_output_video, path_to_output_srt, ad_image=None):

        self.path_to_input_video = path_to_input_video
        self.path_to_input_srt = path_to_input_srt
        self.path_to_output_video = path_to_output_video
        self.path_to_output_srt = path_to_output_srt
        self.stream = Stream(path_to_input_video=self.path_to_input_video, time_resolution=None)

        self.save_path, self.output_filename = os.path.split(path_to_output_video)

        if (ad_image == None):
            dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            ad_image_path = os.path.join(dirname, 'ad_image.png')
            self.ad_image = cv2.imread(ad_image_path)
        else:
            self.ad_image = ad_image

        self.times_of_non_commercial = []

    def concatenate_clips(self):
        list_of_clips = []
        list_of_subs = []

        for times in self.times_of_non_commercial:
            time_of_all_clips_before = 0
            for clip in list_of_clips:
                time_of_all_clips_before += clip.duration

            list_of_clips.append(VideoFileClip(self.path_to_input_video).subclip(times[0], times[1]))
            list_of_subs.append(SubtitleManager(self.path_to_input_srt).subclip(times[0],times[1],time_of_all_clips_before))


        final_clip = concatenate_videoclips(list_of_clips)
        final_srt = concatenate_subtitles(list_of_subs)
        final_clip.write_videofile(self.path_to_output_video)

        SubtitlesClip(subtitles=final_srt).write_srt(self.path_to_output_srt)

        return True

    def remove_frames_with_commercial_break_in_progress(self):

        frame = self.stream.readNextFrameFromVideo()

        progress_bar = tqdm(total=self.stream.time_in_seconds * self.stream.frameReader.videoFPS)

        ad_image_resized = cv2.resize(self.ad_image, dsize=None, fx=0.25, fy=0.25)
        ad_image_cropped = crop_image_to_percent(img=ad_image_resized, axis='y', part_image='bottom', percentage=0.65)
        ad_image_cropped = crop_image_to_percent(img=ad_image_cropped, axis='y', part_image='top', percentage=0.35)

        time_tup = [0.0, None]
        ad_off = True

        while not self.stream.videoFinished:

            frame_resized = cv2.resize(frame, dsize=None, fx=0.25, fy=0.25)
            cropped_frame = crop_image_to_percent(img=frame_resized, axis='y', part_image='bottom', percentage=0.65)
            cropped_frame = crop_image_to_percent(img=cropped_frame, axis='y', part_image='top', percentage=0.35)

            ssim_measure = compare_ssim(X=cropped_frame, Y=ad_image_cropped, multichannel=True)

            if (ssim_measure > 0.6):
                if (ad_off):
                    time_tup[1] = self.stream.getTimeOfFrameInSeconds() - self.stream.time_resolution
                    ad_off = False

                frame = self.stream.readNextFrameFromVideo()
                progress_bar.update(1)
                continue
            else:
                if (not ad_off):
                    self.times_of_non_commercial.append(time_tup)
                    time_tup = [self.stream.getTimeOfFrameInSeconds(), None]
                    ad_off = True

            frame = self.stream.readNextFrameFromVideo()
            progress_bar.update(1)

        progress_bar.close()

        if (time_tup[1] == None):
            time_tup[1] = self.stream.time_in_seconds
            self.times_of_non_commercial.append(time_tup)

        print (self.times_of_non_commercial)

        self.concatenate_clips()

        return True
