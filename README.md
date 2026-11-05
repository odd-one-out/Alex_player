# Alex_player
Audio player made with PyQt6

This is my student project - a simple audio player that can play audio tracks. It's written on Python, made with PyQt6.
It has some standart feachers:
1. play, stop, pause a track
2. change volume level
3. change track tempo (speed)
4. load a folder with tracks or just load one track
5. add tracks to favourites and remove them from there
6. Shows meta info about a track
7. Shows some standart errors via QMessageBox

It's styled with css and qtawesome library
It also includes logger

It works on Ubuntu 24 and Ubuntu 26, though I started to get this error, when running the app in a python venv via vscode:
GLib-GIO-ERROR **: Settings schema 'org.gnome.settings-daemon.plugins.xsettings' does not contain a key named 'antialiasing'
as I understand there is a problem with display server protocols X11 and Wayland.
if I export system's global schema, as Gemini AI advised me, player works.  In terminal print:
export GSETTINGS_SCHEMA_DIR=/usr/share/glib-2.0/schemas

Here is the instruction made with Gemini AI, how to make an executable file for this player:

 1. In terminal go to the root directory of the project and print:
 	pyinstaller --onefile --windowed --name="AudioPlayer" start.py
 	
 2. Open AudioPlayer.spec file (it should appear in the root directory) and configure the datas and hiddenimports parameters:
 	
	a = Analysis(
	    ['start.py'],
	    pathex=[],
	    binaries=[],
	    datas=[('app_styles.qss', '.')],
	    hiddenimports=['player_logger'],
	    hookspath=[],
	    hooksconfig={},
	    runtime_hooks=[],
	    excludes=[],
	    noarchive=False,
	    optimize=0,
	)
	
 3. In terminal print:
 	pyinstaller AudioPlayer.spec

4. In the 'dist' folder you'll see the executable file - AudioPlayer) 
