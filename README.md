# clockshortenstream
A package to shorten the NHL hockey stream into sequences containing only gameplay


IMPORTANT: 
---------
This is written in Py 2.7. You will need python-opencv installed


INSTALLATION:
-------------
Download the source files

Navigate to the folder where setup.py lies in your terminal

Do: pip install -e .

(This will create a package in your python environment called clockshortenstream using a symlink. So anytime we make changes in this code, you can just pull the repo to ths same spot and the python package will be updated automatically without re-installing it)

USAGE:
------
```
from clockshortenstream.process_video_pkg.clock_processes import ShortenVideoStream,CommercialRemoverBasic

path_to_input_video = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/SJS-CAR-HOME.mp4'
path_to_input_video_srt = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/SJS-CAR-HOME.srt'

path_to_shortened_video = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/shortened_video.mp4'
path_to_shortened_video_srt = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/shortened_video.srt'

svs = ShortenVideoStream(path_to_input_video=path_to_input_video, path_to_input_srt=path_to_input_video_srt, commercial_removed=False)
svs.shorten_video_stream( path_to_output_video=path_to_shortened_video, path_to_output_srt=path_to_shortened_video_srt)
```
