from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from chunithm import app
from chunithm import db
from chunithm import models

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def test_data():
    """Create a test user"""
    db.create_all()
    new_user = models.User('hoge','hoge')
    db.session.add(new_user)
    db.session.commit()


if __name__ == '__main__':
    manager.run()