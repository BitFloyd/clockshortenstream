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

path_to_input_video = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/SJS-CAR-HOME_com_brk_removed.mp4'
path_to_video_wo_commercial = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/SJS-CAR-HOME-no-commercial.mp4'
path_to_shortened_video = '/home/seby/Seby Main/PhD/REPOSITORY/test_data/SJS-CAR-HOME-shortened.mp4'

commRemover = CommercialRemoverBasic(path_to_input_video=path_to_input_video,path_to_output_video=path_to_video_wo_commercial)
commRemover.remove_frames_with_commercial_break_in_progress()

svs = ShortenVideoStream(path_to_input_video=path_to_video_wo_commercial)
svs.shorten_video_stream(path_to_output_video=path_to_shortened_video)
```
