import os, sys

# files player.log and favourites will be saved in the home directory, in the folder .config (where other system apps files are saved, too)
#  and folder AudioPLayer: ~/.config/AudioPlayer
def get_app_data_dir(app_name="AudioPlayer"):
    """Returns a persistent directory path for logs and settings on Linux."""
    # Fallback to standard ~/.config/app_name if XDG environment variable isn't set
    base_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    app_dir = os.path.join(base_dir, app_name)
    
    # Safely create the folder if it does not exist yet
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def resource_path(relative_path):
    """Get absolute path to read-only bundled assets (like styles.qss)"""
    try:
        return os.path.join(sys._MEIPASS, relative_path)
    except AttributeError:
        return os.path.abspath(relative_path)