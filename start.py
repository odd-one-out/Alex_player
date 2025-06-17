import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QListWidget, QFileDialog, QSlider, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# QWidget (and my class AudioApp) creates the main window where all other widgets work


# Main app class
class AudioApp(QWidget):

    def __init__(self):
        super().__init__()

        #settings
        self.setWindowTitle = "Roxy-Drive"
        self.setGeometry(100, 300, 400, 200)
        self.set_gui()
        self.set_audio()
        self.css_styles()
        self.event_handler()

        # elements
    def set_gui(self):

        # title
        self.title = QLabel('Roxy audio player')
        self.title.setObjectName('title')
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # tracks window
        self.file_list = QListWidget()

        # buttons
        #self.btn_file_opener = QPushButton('Choose a track')
        #self.btn_file_opener.setObjectName('btn-open')
        self.btn_play = QPushButton('PLAY')
        self.btn_pause = QPushButton('PAUSE')
        self.btn_stop = QPushButton('STOP')

        # deactivate btns at first
        self.btn_pause.setDisabled(True)
        self.btn_stop.setDisabled(True)
        
        # slider for speed
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.speed_slider.setTickInterval(10)
        self.speed_slider_label = QLabel(f'Speed {self.speed_slider.value()}%')


        #slider for duration
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setRange(0,0)
        


        # main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName('main-layout')
        self.main_layout.addWidget(self.title)
        

        # row1 = QHBoxLayout()
        # row1.addWidget(self.btn_file_opener)
        # row1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.main_layout.addLayout(row1)

        self.main_layout.addWidget(self.file_list)
        self.main_layout.addWidget(self.duration_slider)

        # add buttons
        row = QHBoxLayout()
        row.addWidget(self.btn_play)
        row.addWidget(self.btn_pause)
        row.addWidget(self.btn_stop)
        self.main_layout.addLayout(row)

        # add speed slider
        row2 = QHBoxLayout()
        row2.addWidget(self.speed_slider_label)
        row2.addWidget(self.speed_slider)
        self.main_layout.addLayout(row2)

        
        self.setLayout(self.main_layout)


    def set_audio(self):
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

    def css_styles(self):
        self.setStyleSheet("""
                        #main-layout{
                           background-color: white;
                           border: 2px solid grey;
                           }

                        QPushButton{
                        background-color: rgb(45, 97, 100);
                        padding: 10px;
                        border: 1px solid #26422e;
                        border-radius: 20px;
                        }
                        
                        QPushButton:hover {
                        background-color: rgb(33, 72, 74);
                        }
                           


                        QListWidget{
                        background-color: #161716;
                        border: 2px solid #272928;
                        }

                        #title{
                        font-size: 20px;
                        padding-top: 0;
                        padding-bottom: 20px;
                        }
                        """)
                        # #btn-open{
                        # padding: 5px;
                        # border-radius: 10px;
                        #    }

    # event handler
    def event_handler(self):
        #self.btn_file_opener.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)

        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.duration_slider.sliderMoved.connect(self.update_position)

        self.speed_slider.valueChanged.connect(self.update_speed)
        self.speed_slider.sliderMoved.connect(self.update_speed)
        
    #def open_file(self):

        #file_dialog = QFileDialog()
        #file_dialog.setOptions(QFileDialog.Option.DontUseNativeDialog) - if the window doesn't open or other problems with it
        # path = QFileDialog.getExistingDirectory(self, 'Select folder')

        # if path:
        #     self.file_list.clear()
        #     for f in os.listdir(path):
        #         print(f)
        #         if f.endswith('.mp3') or f.endswith('.wave'):
        #             self.file_list.addItem(f)
        # else:


    
    def play(self):
        # if self.file_list.selectedItems():
        #     file_name = self.file_list.selectedItems()[0].text()
        #     print(file_name, type(file_name))
        #     path = QFileDialog.getExistingDirectory(self, 'Select folder')
        #     print(path, type(path))
        #     full_path  = os.path.join(path, file_name)
        #     file_url = QUrl.fromLocalFile(full_path)

        #     self.media_player.setSource(file_url)
        file, _ = QFileDialog.getOpenFileName(self, 'Select track', filter='Audio Files (*.mp3)')
        if file:
            self.file_list.clear()
            self.file_list.addItem(os.path.basename(file))
            self.media_player.setSource(QUrl.fromLocalFile(file))
            self.btn_play.setEnabled(True)
            self.media_player.setPlaybackRate(self.speed_slider.value()*.01)
            self.media_player.play()

            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.btn_play.setDisabled(True)


    def pause(self):
        self.media_player.pause()

        self.btn_pause.setDisabled(True)
        self.btn_play.setEnabled(True)
        

    def stop(self):
        if self.media_player.isPlaying():
            self.media_player.stop()

        self.media_player.setPosition(0)
        self.media_player.setPlaybackRate(self.speed_slider.value()*.01)

        self.btn_pause.setDisabled(True)
        self.btn_stop.setDisabled(True)
        self.btn_play.setEnabled(True)


    def update_speed(self, position):
        self.speed_slider.setValue(position)
        print(position)
        self.media_player.setPlaybackRate(self.speed_slider.value()*.01)
        self.speed_slider_label.setText(f'Speed {self.speed_slider.value()}%')

  
    def update_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        self.duration_slider.setValue(position)
  
    def duration_changed(self, duration):
        self.duration_slider.setRange(0, duration)
        


        










if __name__ == '__main__':
    app = QApplication([])
    main = AudioApp()
    main.show()
    app.exec()

