from flask import current_app as app
from flask import render_template
from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import abort
from chunithm import func
from chunithm import db
from chunithm import chunithm
import hashlib

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/chunithm.api', methods=['POST', 'GET'])
def api():
    if request.method == 'POST':
        user_id = func.extraction_user_id(request.form['userid'])
        if user_id is None:
            abort(400)
        user = chunithm.Calculate(user_id)
        user_hash = user.run()
        return redirect('/chunithm/user/' + user_hash)
    else:
        return abort(403)


@views.route('/chunithm/user/<user_hash>')
@views.route('/chunithm/user/<user_hash>/best')
@views.route('/chunithm/user/<user_hash>/best/<sort>')
def best(user_hash, sort='rate'):
    user = db.User(user_hash)
    user_best = user.load_best()
    user_info = user.load_user()
    if user_best and user_info:
        return render_template('main.html')


@views.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['UserName'] == app.config['USERNAME']:
            if hashlib.sha3_512(str(request.form['Password']).encode('utf8')).hexdigest() == app.config['PASSWORD']:
                session['logged_in'] = True
                return redirect('/admin')
        return render_template('Login.html',Error='Invalid UserName or Password')
    else:
        if 'logged_in' in session and session['logged_in'] is True:
            return redirect('/admin')            
        return render_template('login.html')

@views.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@views.route('/admin')
def admin():
    if 'logged_in' in session and session['logged_in'] is True:
        return render_template('admin.html')
    return redirect('/login')