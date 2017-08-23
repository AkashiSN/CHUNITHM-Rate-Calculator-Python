from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from chunithm import app
from chunithm import db
from chunithm import models
from chunithm import func

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def Admin(password):
    """Create a admin user"""
    db.create_all()
    new_user = models.User('admin', password)
    db.session.add(new_user)
    db.session.commit()

@manager.command
def Register_music(sega_id, password):
    """初回実行時に楽曲のデータベースを"""
    user_id = func.fetch_user_id(sega_id, password)
    for music_level in range(11,15):
        music_id_list = func.fetch_music_level_list(user_id, music_level)
        for plus in ("levelList","levelPlusList"):
            for music_id in music_id_list[plus]:
                fetch_data = func.fetch_music_score_highest(user_id, music_id)
                plus_list = {"levelList": '', "levelPlusList": '+'}
                music = {
                    'music_id': music_id,
                    'music_name': fetch_data['musicName'],
                    'music_cover_image': fetch_data['musicFileName'],
                    'music_artist_name': fetch_data['artistName'],
                    'music_difficulty': music_id_list['difLevelMap'][str(music_id)],
                    'music_level': str(music_level)+plus_list[plus],
                    'music_base_rate': 0
                }
                new_music = models.Music(music)
                db.session.add(new_music)
                db.session.commit()


if __name__ == '__main__':
    manager.run()
