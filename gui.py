import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
import sys
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout

from tag_funcs import *

import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
import sys
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QLabel
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

from tag_funcs import *
class Form(QDialog):

    def __init__(self, mp3s, parent=None):
        super(Form, self).__init__(parent)
        self.mp3s = mp3s
        # get music data for first file
        self.num_mp3s = len(mp3s)
        self.file_index = 1
        self.mp3 = mp3s.pop()
        self.tags, self.recognize_generator = self.get_mp3_data(self.mp3)
        # parameters to add audio playback
        self.audio_playing = False
        self.audio = AudioSegment.from_mp3(self.mp3.path)
        self.playback = None

        # setup layout
        self.setWindowTitle("Tag Setter")
        self.layout = QFormLayout(self)

        self.add_all_widgets()

        self.setLayout(self.layout)

    
    def start_stop_audio_playback(self):
        # Turn on audio
        if not self.audio_playing:
            self.audio_playing = True
            self.playback = _play_with_simpleaudio(self.audio)
        # turn off audio
        else:
            self.playback.stop()
            self.audio_playing = False
    def remove_all_widgets(self):
        # for i in reversed(range(self.layout.count())): 
        #     child = self.layout.takeAt()
            # self.layout.itemAt(i).widget().setParent(None)
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
              child.widget().deleteLater()

    def add_all_widgets(self):
        #setup buttons       
        self.confirm_button = QPushButton("Confirm")
        self.skip_button = QPushButton("Skip")
        self.requery_shazam_button = QPushButton("Querry Shazam Again")
        self.start_stop_audio_button = QPushButton("Play/Stop Audio")

        # adding our widgets
        self.layout.addWidget(QLabel(f"File {self.file_index} / {self.num_mp3s}"))
        self.layout.addWidget(QLabel(self.mp3.path))

        self.tag_editor = {}
        for key, value in self.tags.items():
            self.tag_editor[key] = QLineEdit(value)
            self.layout.addRow(key, self.tag_editor[key])

        # layout.addWidget(QLineEdit("Write my name here.."))
        self.layout.addWidget(self.confirm_button)
        self.layout.addWidget(self.skip_button)
        self.layout.addWidget(self.requery_shazam_button)
        self.layout.addWidget(self.start_stop_audio_button)
        # self.layout.addWidget(self.start_stop_audio_button, alignment=QtCore.Qt.AlignRight)

        # button function connections
        self.confirm_button.clicked.connect(self.set_tags_and_get_next)
        self.skip_button.clicked.connect(self.get_next_mp3)
        self.requery_shazam_button.clicked.connect(self.requery_shazam)
        self.start_stop_audio_button.clicked.connect(self.start_stop_audio_playback)


    def reset_widgets(self):
        self.remove_all_widgets()
        self.add_all_widgets()

    def requery_shazam(self):
        mp3_json = query_shazam(self.recognize_generator)
        self.tags = get_audio_tags_from_json(mp3_json)
        self.reset_widgets()

    def set_tags_and_get_next(self):
        
        self.tags = {key: value.text() for key, value in self.tag_editor.items()}
        self.close()
        self.reset_widgets()
        set_mp3_tags(self.mp3, False, self.tags)
        self.get_next_mp3()
        self.show()

    def print_widgets(self):
        for key, value in self.tags.items():
            print(value.text())

    def get_next_mp3(self):
        if self.num_mp3s == self.file_index:
            QApplication.quit()
            
        if self.playback is not None:
            self.playback.stop()
        self.close()
        self.mp3 = self.mp3s.pop()
        self.file_index += 1
        self.tags, self.recognize_generator = self.get_mp3_data(self.mp3)
        self.audio = AudioSegment.from_mp3(self.mp3.path)
        self.reset_widgets()
        self.show()

    def get_mp3_data(self, mp3):
        recognize_generator = setup_mp3_for_Shazam(mp3)
        mp3_json = query_shazam(recognize_generator) # current offset & shazam response to recognize requests
        tags = get_audio_tags_from_json(mp3_json)
        return tags, recognize_generator

def make_parser():
    parser = argparse.ArgumentParser(
                    prog = 'Set MP3 Tags',
                    description = 'Takes an MP3. Querries ShazamAPI to get the tags, and sets the tags')

    parser.add_argument("-d", "--directory", default='/home/jack/Music/mp3s/')
    parser.add_argument("-a", "--all_files_in_directory", action="store_true", default=True)
    parser.add_argument("-o", "--overwrite_tags", action="store_true", default=False)
    parser.add_argument("-s", "--skip_manual_verification", action="store_true", default=False)
    parser.add_argument("-f", "--filename")
    return parser

if __name__ == '__main__':
    parser = make_parser()
    # Create the Qt Application
  
    
    args = parser.parse_args()

    if args.all_files_in_directory:
        # get all mp3 objects
        mp3s = get_mp3s(args.directory)
    else: 
        mp3s = [eyed3.load(args.directory + args.filename)]

    # filter out mp3s that already have tags, unless we want to overwrite them
    mp3s = [mp3 for mp3 in mp3s if not has_tags(mp3)] if not args.overwrite_tags else mp3s
    app = QApplication(sys.argv)

    # Create and show the form
    form = Form(mp3s)
    form.show()
    # # filter out mp3s that already have tags, unless we want to overwrite them


    # # Run the main Qt loop
    sys.exit(app.exec())