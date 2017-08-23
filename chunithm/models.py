from . import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


class Admin(db.Model):
    """管理ユーザーのデータベース"""
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def __repr__(self):
        return '<User {!r}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True)
    music_id = db.Column(db.Integer)
    music_name = db.Column(db.String)
    music_cover_image = db.Column(db.String)
    music_artist_name = db.Column(db.String)
    music_difficulty = db.Column(db.Integer)
    music_level = db.Column(db.String)
    music_base_rate = db.Column(db.Integer)

    def __init__(self, music):
        self.music_id = music['music_id']
        self.music_name = music['music_name']
        self.music_cover_image = music['music_cover_image']
        self.music_artist_name = music['music_artist_name']
        self.music_difficulty = music['music_difficulty']
        self.music_level = music['music_level']
        self.music_base_rate = music['music_base_rate']

    def fetch_music_info(self):
        """
        曲の情報をフェッチし返す
        :param music_id: 楽曲id
        :param music_difficulty: 楽曲の難易度(masterとか)
        :return music: 楽曲の情報
        """
        music = {
            'id': self.id,
            'music_id': self.music_id,
            'music_name': self.music_name,
            'music_cover_image': self.music_cover_image,
            'music_artist_name': self.music_artist_name,
            'music_difficulty': self.music_difficulty,
            'music_level': self.music_level,
            'music_base_rate': self.music_base_rate
        }
        return music

    def update_music_info(self):
        """
        楽曲情報を更新する
        :param music: 楽曲情報
        :param music_shortage: 不足分の楽曲情報
        """

