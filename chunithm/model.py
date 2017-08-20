from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text

db = SQLAlchemy(app)


class Music(db.Model):
    __tablename__ = 'music'
    id = Column(Integer, primary_key=True)
    music_id = Column(Integer)
    music_name = Column(Text)
    music_cover_image = Column(Text)
    music_artist_name = Column(Text)
    music_difficulty = Column(Integer)
    music_level = Column(Integer)
    music_base_rate = Column(Integer)
