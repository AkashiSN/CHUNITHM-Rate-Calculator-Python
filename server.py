# from chunithm import start_app

# app = start_app()
#
from flask import *
from chunithm import db

app = Flask(__name__)
@app.route('/')
def index():
    database = db.music_base_rate()
    music = {
        'music_id': 417,
        'music_name': "lsj",
        'music_cover_image': "lsjd",
        'music_artist_name': "lks",
        'music_difficulty': 3,
        'music_level': 12,
        'music_base_rate': 12.3
    }
    database.update_music_info(music)
    return "a"
app.run(debug=True, threaded=True, host="0.0.0.0", port=5555)