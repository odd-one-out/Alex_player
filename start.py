from pathlib import Path
from os.path import basename
from datetime import timedelta

import qtawesome as qta

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QListWidget, QFileDialog, QSlider, QVBoxLayout, QHBoxLayout, QStyleFactory, QStyle
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudio, QMediaMetaData

# QWidget (and my class AudioApp) creates the main window where all other widgets work


# custom slider
class MouseSlider(QSlider):
    #sliderClicked = pyqtSignal(int)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            value = QStyle.sliderValueFromPosition(
                    self.minimum(), self.maximum(), event.pos().x(), self.width()
                )
            # event.accept()
            # x = event.pos().x()
            # value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            #self.sliderClicked.emit(value)
            self.setValue(value)
        super().mousePressEvent(event)


# Main app class
class AudioApp(QWidget):

    def __init__(self):
        super().__init__()

        #settings
        self.setWindowTitle = "Roxy-Drive"
        self.setGeometry(100, 300, 500, 200)
        self.set_gui()
        self.css_styles()
        self.event_handler()

        # elements
    def set_gui(self):

        # title
        self.title = QLabel('Roxy audio player')
        self.title.setObjectName('title')
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # tracklist
        self.playlist = []

        # tracklist window
        self.track_list = QListWidget()

        # buttons
        self.btn_folder_opener = QPushButton('Select folder')
        self.btn_folder_opener.setObjectName('btn-open')
        self.btn_track_opener = QPushButton('Select track')
        self.btn_track_opener.setObjectName('btn-open')

        play_icon = qta.icon('mdi.play', scale_factor=2.0)
        self.btn_play = QPushButton(play_icon, '')

        next_icon = qta.icon('mdi.fast-forward', scale_factor=1.5)
        self.btn_next = QPushButton(next_icon, '')

        prev_icon = qta.icon('mdi.rewind', scale_factor=1.5)
        self.btn_previous = QPushButton(prev_icon, '')

        pause_icon = qta.icon('mdi.pause', scale_factor=2.0)
        self.btn_pause = QPushButton(pause_icon, '')

        stop_icon = qta.icon('mdi.stop', scale_factor=2.0)
        self.btn_stop = QPushButton(stop_icon, '')

        # deactivate btns at first
        self.btn_play.setDisabled(True)
        self.btn_pause.setDisabled(True)
        self.btn_stop.setDisabled(True)
        self.btn_previous.setDisabled(True)
        self.btn_next.setDisabled(True)
        
        # slider for speed
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.speed_slider.setTickInterval(10)
        self.speed_slider_label = QLabel(f'Speed {self.speed_slider.value()}%')

        # return slider to default
        default_speed_icon = qta.icon('mdi6.backup-restore', scale_factor=1.5)
        self.btn_default_speed = QPushButton(default_speed_icon, '')
        self.btn_default_speed.setObjectName('default-speed')

        #slider for duration
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setRange(0,0)

        # timer
        self.cur_time_label = QLabel('00:00:00')

        # meta label
        self.meta_label = QLabel()

        #volume slider
        self.volume_slider = MouseSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setValue(50)
        self.volume_label = QLabel('Volume')
        

        #audio
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(self.real_volume(self.volume_slider.value()))
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)


        # main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName('main-layout')

        # add name
        r = QVBoxLayout()
        r.setContentsMargins(20, 0, 20, 0)
        r.addWidget(self.title)
        self.main_layout.addLayout(r)
        
        # add open buttons
        row1 = QHBoxLayout()
        row1.addWidget(self.btn_folder_opener, alignment=Qt.AlignmentFlag.AlignLeft)
        row1.addWidget(self.btn_track_opener, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(row1)


        # add playlist, duration_slider, timer, meta
        self.main_layout.addWidget(self.track_list)
        self.main_layout.addWidget(self.duration_slider)
        self.main_layout.addWidget(self.cur_time_label)
        self.main_layout.addWidget(self.meta_label)

        # add buttons
        row = QHBoxLayout()
        row.addWidget(self.btn_previous)
        row.addWidget(self.btn_play)
        row.addWidget(self.btn_next)
        row.addWidget(self.btn_pause)
        row.addWidget(self.btn_stop)
        self.main_layout.addLayout(row)

        # add speed slider
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 20, 0, 20)
        row2.addWidget(self.speed_slider_label)
        row2.addWidget(self.speed_slider)
        row2.addWidget(self.btn_default_speed)
        self.main_layout.addLayout(row2)

        # add volume slider
        row3 = QHBoxLayout()
        row3.addWidget(self.volume_label)
        row3.addWidget(self.volume_slider)
        self.main_layout.addLayout(row3)


        self.setLayout(self.main_layout)


    def css_styles(self):
        try:
            with open('app_styles.qss') as f:
                styles = f.read()
                self.setStyleSheet(styles)
        except (FileExistsError, FileNotFoundError, PermissionError) as e:
            print(str(e))
        except Exception as ex:
            print('some mistake occured')

    
    # event handler
    def event_handler(self):
        self.btn_folder_opener.clicked.connect(self.open_folder)
        self.btn_track_opener.clicked.connect(self.open_track)

        self.track_list.itemClicked.connect(self.choose_track)

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_previous.clicked.connect(self.previous_song)
        self.btn_next.clicked.connect(self.next_song)
        self.btn_stop.clicked.connect(self.stop)

        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.duration_slider.sliderMoved.connect(self.update_position)

        self.speed_slider.valueChanged.connect(self.update_speed)
        self.speed_slider.sliderMoved.connect(self.update_speed)
        self.btn_default_speed.clicked.connect(self.speed_to_default)
        
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.sliderMoved.connect(self.set_volume)

        self.media_player.metaDataChanged.connect(self.meta_set)

        self.media_player.mediaStatusChanged.connect(self.song_ended)
        
    def open_folder(self):
        suffixies = ('.mp3', '.wave', '.wav', '.m4a', '.aac', '.flac')
        path = QFileDialog().getExistingDirectory(self, 'Select folder')
        if path:
            self.playlist.clear()
            self.track_list.clear()
            for f in Path(path).iterdir():
                print(f)
                if f.suffix in suffixies:
                    self.playlist.append(str(f))
                    self.track_list.addItem(str(f.name))
        print(self.track_list)


        # music_folder = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.MusicLocation)
        # print(music_folder[0])
        # file_dialog.setDirectory(music_folder[0])
        # urls = file_dialog.selectedUrls()
        # print(urls)
        #file_dialog.setOptions(QFileDialog.Option.DontUseNativeDialog) - if the window doesn't open or other problems with it

    def open_track(self):
        audioFormats = "*.mp3 *.wav *.wave *.aac *.m4a *.flac"
        file, _ = QFileDialog.getOpenFileName(self, 'Select track', filter='Audio Files ({audioFormats})')
        if file:
            self.playlist.clear()
            self.track_list.clear()
            self.playlist.append(file)
            self.track_list.addItem(basename(file))
            self.media_player.setSource(QUrl.fromLocalFile(file))
            self.btn_play.setEnabled(True)
        

    def choose_track(self):
        id = self.track_list.currentRow()
        print(f'current id is {id}')
        self.media_player.setSource(QUrl.fromLocalFile(self.playlist[id]))
        self.btn_play.setEnabled(True)
        self.btn_previous.setEnabled(True)
        self.btn_next.setEnabled(True)

        #metadata
        self.meta_set()

        self.play()


    def play(self):
        self.media_player.setPlaybackRate(self.speed_slider.value()*.01)
        self.media_player.play()
        print(f'duration on play is {self.media_player.duration()}')

        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_play.setDisabled(True)


    def meta_set(self):
        meta = self.media_player.metaData()
        title = meta.value(QMediaMetaData.Key.Title)
        author = meta.value(QMediaMetaData.Key.Author)
        print(title, author)
        self.meta_label.setText(f'song: {title}\nartist: {author}')
            
        
    def pause(self):
        self.media_player.pause()
        self.btn_play.setDisabled(False)
        self.btn_pause.setDisabled(True)
        

    def stop(self):
        if self.media_player.isPlaying():
            self.media_player.stop()
        dur = self.media_player.duration()
        print(f'duration on stop - {dur}')
        self.media_player.setPosition(0)
        self.media_player.setPlaybackRate(self.speed_slider.value()*.01)

        self.btn_pause.setDisabled(True)
        self.btn_stop.setDisabled(True)
        self.btn_play.setEnabled(True)

    def previous_song(self):
        current_id = self.track_list.currentRow()
        if current_id == 0:
            prev_id = self.track_list.count() - 1
        else:
            prev_id = current_id - 1
        self.media_player.setSource(QUrl.fromLocalFile(self.playlist[prev_id]))
        self.track_list.setCurrentRow(prev_id)
        self.play()

    def next_song(self):
        current_id = self.track_list.currentRow()
        count = self.track_list.count()
        if current_id == count-1:
            next_id = 0
        else:
            next_id =  current_id + 1
        self.media_player.setSource(QUrl.fromLocalFile(self.playlist[next_id]))
        self.track_list.setCurrentRow(next_id)
        self.play()

    def song_ended(self, status):
        if status == self.media_player.MediaStatus.EndOfMedia:
            self.next_song()


    def update_speed(self, position):
        self.speed_slider.setValue(position)
        print(position)
        self.media_player.setPlaybackRate(self.speed_slider.value()*.01)
        self.speed_slider_label.setText(f'Speed {self.speed_slider.value()}%')

    def speed_to_default(self):
        self.speed_slider.setSliderPosition(100)
  
    def update_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        self.duration_slider.setValue(position)
        track_time = str(timedelta(seconds=round(self.duration_slider.value() / 1000)))
        self.cur_time_label.setText(track_time)
  
    def duration_changed(self, duration):
        self.duration_slider.setRange(0, duration)

    def real_volume(self, slider_value):
        return QAudio.convertVolume(
            slider_value * .01, 
            QAudio.VolumeScale.LogarithmicVolumeScale, 
            QAudio.VolumeScale.LinearVolumeScale
        )

    def set_volume(self, volume):
        self.audio_output.setVolume(self.real_volume(volume))
        




if __name__ == '__main__':
    app = QApplication([]) # отвечает за все события в приложении
    print(app.style().objectName()) #узнать какой сейчас стиль  - fusion
    print(QStyleFactory.keys()) # узнать все возможные для меня стили ('windows', 'Fusion')
    main = AudioApp()
    main.show()
    app.exec()


