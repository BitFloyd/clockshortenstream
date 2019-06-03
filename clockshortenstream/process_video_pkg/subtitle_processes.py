from commentaryanalysis.cleanSRT import read_and_clean_srt
from datetime import time

def time_to_string(t):
    h = int(t/3600)
    m = int((t - h*3600)/60)
    s = int(t - h*3600 - m*60)
    ms = int((t - int(t))*1e6)
    t_value = time(h,m,s,ms)
    return t_value.strftime('%H:%M:%S,%f')

def time_to_seconds(t):

    return t.hour*3600 + t.minute*60 + t.second + t.microsecond/(10e6)

class SubtitlesClip():
    """ A Clip that serves as "subtitle track" in videos.

    One particularity of this class is that the images of the
    subtitle texts are not generated beforehand, but only if
    needed.

    Parameters
    ==========

    subtitles
      Either the name of a file, or a list

    """

    def __init__(self, subtitles):

        if isinstance(subtitles, str):
            subtitles = read_and_clean_srt(subtitles)
            subtitles = zip(subtitles.keys(),subtitles.values())

        self.subtitles = subtitles

        self.start = 0
        self.duration = max([tb for ((ta, tb), txt) in self.subtitles])
        self.end = self.duration



    def in_subclip(self, t_start=None, t_end=None):
        """ Returns a sequence of [(t1,t2), txt] covering all the given subclip
        from t_start to t_end. The first and last times will be cropped so as
        to be exactly t_start and t_end if possible. """

        subclip = []

        for ((t1, t2), txt) in self.subtitles:
           if(time_to_seconds(t1)>=t_start and time_to_seconds(t2) <=t_end):
                subclip.append(((t1,t2),txt))

        return subclip



    def __iter__(self):
        return self.subtitles.__iter__()

    def __getitem__(self, k):
        return self.subtitles[k]

    def __str__(self):

        def to_srt(sub_element):
            (ta, tb), txt = sub_element
            fta, ftb = map(time_to_string, (ta, tb))
            return "%s --> %s\n%s" % (fta, ftb, txt)

        return "\n\n".join(map(to_srt, self.subtitles))




class SubtitleManager:

    def __init__(self,sub_filename):
        self.sub_filename = sub_filename
        self.sub = SubtitlesClip(self.sub_filename)

    def subclip(self,t_start,t_end,t_prev):

        self.subs_in_clip = self.sub.in_subclip(t_start,t_end)

        self.adjusted_subs = []

        for ((i,j),txt) in self.subs_in_clip:

            new_time_start = time_to_seconds(i)-t_start+t_prev
            new_time_end = time_to_seconds(j)-t_start+t_prev

            line = txt

            self.adjusted_subs.append(((new_time_start,new_time_end),line))

        return self.adjusted_subs



def concatenate_subtitles(list_of_subs):

    final_subs = []
    for subs in list_of_subs:
        final_subs.extend(subs)

    return final_subs

def write_to_subtitle_file(final_subs,filename):
    counter = 1
    with open(filename, 'w+') as f:
        for ((ta, tb), txt)in final_subs:
            fta, ftb = map(time_to_string, (ta, tb))
            f.write("%s\n%s --> %s\n%s\n\n" % (counter, fta, ftb, txt))

            counter += 1


    return True


