from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from chunithm import app
from chunithm import db
from chunithm import models
from chunithm import func
from chunithm.chunithm import Manage

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def Admin(password):
    """Create a admin user"""
    db.create_all()
    new_user = models.Admin('admin', password)
    db.session.add(new_user)
    db.session.commit()

@manager.command
def Register_music(sega_id, password):
    """初回実行時に楽曲のデータベースを作成"""
    user_id = func.fetch_user_id(sega_id, password)
    manage = Manage()
    manage.check_music_list(user_id)

if __name__ == '__main__':
    manager.run()
