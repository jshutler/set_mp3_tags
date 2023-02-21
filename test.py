import os
from pydub.playback import _play_with_simpleaudio
from time import sleep
mp3s = os.listdir('../mp3s')
mp3 = mp3s[0]

from pydub import AudioSegment

audio = AudioSegment.from_mp3("../mp3s/" + mp3)
playback = _play_with_simpleaudio(audio)

sleep(5)

playback.stop()
playback.stop()