from pathlib import Path
from os.path import basename
from datetime import timedelta

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QListWidget,
    QFileDialog,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QStyle,
    QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudio, QMediaMetaData
from PyQt6.QtGui import QColor

import qtawesome as qta

import shelve
file = 'favourite_hits'

from player_logger import logger, logger_decor


# QWidget (and my class AudioApp) creates the main window where all other widgets work

# custom slider used for volume slider
class MouseSlider(QSlider):

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = QStyle.sliderValueFromPosition(
                    self.minimum(), self.maximum(), event.pos().x(), self.width()
                )
            self.setValue(value)
        super().mousePressEvent(event)


# Main app class
class AudioApp(QWidget):

    def __init__(self):
        super().__init__()

        #settings
        self.setWindowTitle("Alex audio player")
        self.setGeometry(100, 300, 500, 200)
        self.set_gui()
        self.css_styles()
        self.event_handler()

    # elements
    @logger_decor
    def set_gui(self):

        # title
        self.title = QLabel('Alex audio player')
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
        self.btn_favs = QPushButton('Favourites')
        self.btn_favs.setObjectName('btn-open')

        # buttons for favourite tracks
        favs_add = qta.icon('mdi6.heart-plus', color=QColor(185, 78, 187), color_active='purple')
        self.btn_add_to_favs = QPushButton(favs_add, '')
        self.btn_add_to_favs.setIconSize(QSize(25, 25))
        favs_remove = qta.icon('mdi6.heart-remove', color=QColor(185, 78, 187), color_active='purple')
        self.btn_remove_from_favs = QPushButton(favs_remove, '')
        self.btn_remove_from_favs.setIconSize(QSize(25, 25))

        # player buttons
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
        self.btn_add_to_favs.setDisabled(True)
        self.btn_remove_from_favs.setDisabled(True)
        
        # slider for speed
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(100)
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

        # add title
        r = QVBoxLayout()
        r.setContentsMargins(20, 0, 20, 0)
        r.addWidget(self.title)
        self.main_layout.addLayout(r)
        
        # add buttons for opening a folder or a track
        row1 = QHBoxLayout()
        row1.addWidget(self.btn_folder_opener, alignment=Qt.AlignmentFlag.AlignLeft)
        row1.addWidget(self.btn_track_opener, alignment=Qt.AlignmentFlag.AlignLeft)
        row1.addWidget(self.btn_favs, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(row1)


        # add playlist
        self.main_layout.addWidget(self.track_list)

        # add fav_buttons
        favs_row = QHBoxLayout()
        favs_row.setAlignment(Qt.AlignmentFlag.AlignRight)
        favs_row.addWidget(self.btn_add_to_favs, alignment=Qt.AlignmentFlag.AlignRight)
        favs_row.addWidget(self.btn_remove_from_favs, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(favs_row)

        # add duration_slider, timer, meta       
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
            QMessageBox.warning(self, 'no styles', 'sorry, unable to style your player')
            logger.exception('css not found or no permission: %s', e)
        except Exception as ex:
            QMessageBox.warning(self, 'no styles', 'sorry, unable to style your player')
            logger.exception('impossible to load css - %s', ex)

    
    # event handler
    def event_handler(self):
        self.btn_folder_opener.clicked.connect(self.open_folder)
        self.btn_track_opener.clicked.connect(self.open_track)
        self.btn_favs.clicked.connect(self.load_favs)
        self.btn_add_to_favs.clicked.connect(self.add_fav)
        self.btn_remove_from_favs.clicked.connect(self.remove_fav)

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


    def iter_folder(self, path):
        suffixies = ('.mp3', '.wave', '.wav', '.m4a', '.aac', '.flac')
        for f in Path(path).iterdir():
            if f.is_dir():
                logger.info('itering folder - %s', f)
                self.iter_folder(f)
            else:
                logger.info('itering file - %s', f)
                if f.suffix in suffixies:
                    self.playlist.append(str(f))
                    self.track_list.addItem(f.name)
    
    def open_folder(self):
        try:
            path = QFileDialog().getExistingDirectory(self, 'Select folder')
            if path:
                self.playlist.clear()
                self.track_list.clear()
                self.iter_folder(path) 
                logger.info('track list loaded - %s', self.track_list)
                if len(self.track_list) == 0:
                    QMessageBox.warning(self, 'no music!', 'no music found in this folder, try another one')
                    logger.info('folder has no music files, track list is empty - %s', self.track_list)

        except (FileNotFoundError, FileExistsError) as e:
            QMessageBox.warning(self, 'error', 'unable to open folder')
            logger.exception('unable to open folder', exc_info=True)

    def open_track(self):
        audioFormats = "*.mp3 *.wav *.wave *.aac *.m4a *.flac"
        file, _ = QFileDialog.getOpenFileName(self, 'Select track', filter=f'Audio Files ({audioFormats})')
        if file:
            self.playlist.clear()
            self.track_list.clear()
            self.playlist.append(file)
            self.track_list.addItem(basename(file))
            self.media_player.setSource(QUrl.fromLocalFile(file))
            self.btn_play.setEnabled(True)

    def load_favs(self):
        self.playlist.clear()
        self.track_list.clear()

        try:
            with shelve.open(file) as f:
                for k, v in f.items():
                    self.playlist.append(v)
                    self.track_list.addItem(k)
            logger.info('got from shelve, track list - %s', self.track_list)

        except (FileNotFoundError, FileExistsError) as e:
            QMessageBox.warning(self, 'sorry', 'unable to open favourite_hits')
            logger.exception('shelve data not found', exc_info=True)

    def choose_track(self):
        id = self.track_list.currentRow()
        logger.info('current id is %s', id)
        self.media_player.setSource(QUrl.fromLocalFile(self.playlist[id]))
        self.btn_play.setEnabled(True)
        self.btn_previous.setEnabled(True)
        self.btn_next.setEnabled(True)

        #metadata
        self.meta_set()

        self.play()
        self.btn_add_to_favs.setDisabled(False)
        self.btn_remove_from_favs.setDisabled(False)

    def play(self):
        self.media_player.setPlaybackRate(self.speed_slider.value()*.01)
        self.media_player.play()
        logger.info(f'duration on play is {self.media_player.duration()}')

        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_play.setDisabled(True)

    def meta_set(self):
        meta = self.media_player.metaData()
        title = meta.stringValue(QMediaMetaData.Key.Title)
        author = meta.stringValue(QMediaMetaData.Key.AlbumArtist)
        logger.info('got meta data: title - %s, artist - %s', title, author)
        self.meta_label.setText(f'song: {title if title else 'unknown'}\nartist: {author if author else 'unknown'}')
            
    def pause(self):
        self.media_player.pause()
        self.btn_play.setDisabled(False)
        self.btn_pause.setDisabled(True)
        
    def stop(self):
        if self.media_player.isPlaying():
            self.media_player.stop()
        dur = self.media_player.duration()
        logger.info(f'duration on stop - {dur}')
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
        logger.info('speed slider position - %s', position)
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

    def add_fav(self):
        if self.track_list.currentItem():
            name = self.track_list.currentItem().text()
            id = self.track_list.currentRow()
            path = self.playlist[id]
            with shelve.open(file) as f:
                if not f.get(name):
                    f[name] = path
                    QMessageBox.information(self, 'yeah!', f'track {name} is added to "Favourites"')
                    logger.info('track added to shelve - %s, path - %s', name, path)
                else:
                    QMessageBox.information(self, '', f'track {name} is already in "Favourites"')
                    logger.info('track - %s user tries to add is already in shelve', name)

        else:
            QMessageBox.warning(self, 'wtf?', 'please, choose a track you want to add to "Favourites"')
            logger.warning('user hasn\'t chosen a track to add to favs')
            
    def remove_fav(self):
        if self.track_list.currentItem():
            name = self.track_list.currentItem().text()
            with shelve.open(file) as f:
                if f.get(name):
                    del f[name]
                    QMessageBox.information(self, 'got it!', f'track {name} is removed from "Favourites"')
                    logger.info('track removed from shelve - %s', name)
                else:
                    QMessageBox.warning(self, 'error', 'this track is missing in "Favourites"\ntrack can\'t be removed')
                    logger.warning('user trying to delete track that is missing in favs')

        else:
            QMessageBox.warning(self, 'wtf?', 'please, choose a track you want to remove from "Favourites"')
            logger.warning('user hasn\'t chosen a track to remove from favs')


if __name__ == '__main__':
    try:
        app = QApplication([]) # отвечает за все события в приложении
        #print(app.style().objectName()) #узнать какой сейчас стиль  - fusion
        #print(QStyleFactory.keys()) # узнать все возможные для меня стили ('windows', 'Fusion')
        main = AudioApp()
        main.show()
        app.exec()
    except Exception:
        logger.exception('some strange error', exc_info=True)


