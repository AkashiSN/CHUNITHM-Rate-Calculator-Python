from flask import current_app as app,render_template,Blueprint,request,session,redirect
from jinja2 import FileSystemLoader
from chunithm import func
from chunithm import chunithm
import hashlib

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('index.html')

@views.route('/chunithm.api',methods=['POST', 'GET'])
def api():
    if request.method == 'POST':
        userId = func.userId_Get(request.form['userid'])
        if userId is None:
            return render_template("error.html",Message='送信されたデータにはUserIDが含まれていません。CHUNITHM-NETにログインして実行してください。')
        Hash = chunithm.CalcRate(userId)
        if Hash is None:
            return render_template("error.html",Message='このUserIdは無効です。もう一度CHUNITHM-NETにログインして実行してください。')
        return redirect('/chunithm/user/' + Hash)
    else:
        return abort(403)

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