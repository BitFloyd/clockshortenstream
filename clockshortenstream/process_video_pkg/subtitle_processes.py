from moviepy.video.tools.subtitles import SubtitlesClip


class SubtitleManager:

    def __init__(self,sub_filename):
        self.sub_filename = sub_filename
        self.sub = SubtitlesClip(self.sub_filename)

    def subclip(self,t_start,t_end,t_prev):

        self.subs_in_clip = self.sub.in_subclip(t_start,t_end)

        self.adjusted_subs = []

        for i,j in self.subs_in_clip:

            new_time_start = i[0]-t_start+t_prev
            new_time_end = i[1]-t_start+t_prev

            line = j

            self.adjusted_subs.append([(new_time_start,new_time_end),line])

        return self.adjusted_subs



def concatenate_subtitles(list_of_subs):

    final_subs = []
    for subs in list_of_subs:
        final_subs.extend(subs)

    return final_subs



