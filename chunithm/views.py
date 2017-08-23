from chunithm import app
from chunithm import login_manager
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import abort
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required
from urllib.parse import urlparse
from urllib.parse import urljoin

from chunithm.forms import LoginForm
from chunithm.models import User
from chunithm import func
from chunithm import db
from chunithm import chunithm


@app.route('/')
def home():
    """メインページ"""
    return render_template('home.html')


@app.route('/admin')
@login_required
def admin():
    """管理画面"""
    return render_template('admin.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン"""
    next = request.args.get('next') or ''
    if not is_safe_url(next):
        return abort(400)
    if current_user.is_authenticated:
        return redirect(next)
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user.check_password(password):
                login_user(user)
                app.logger.debug('Logged in user %s', user.username)
                flash('Logged in successfully.', 'success')
                return redirect(next)
            else:
                flash('Username or Password is incorrect.', 'danger')
    flash_errors(form)
    return render_template('login.html', form=form, next=next)


@app.route("/logout")
@login_required
def logout():
    """ログアウト"""
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403

@app.errorhandler(405)
def gateway_error(error):
    return render_template("errors/405.html"), 405

@app.errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html"), 400

@app.errorhandler(500)
def general_error(error):
    return render_template("errors/500.html"), 500

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:

            flash("Error in the {} field - {}".format (getattr(form, field).label.text, error), 'danger')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/chunithm.api', methods=['POST', 'GET'])
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


@app.route('/chunithm/user/<user_hash>')
@app.route('/chunithm/user/<user_hash>/best')
@app.route('/chunithm/user/<user_hash>/best/<sort>')
def best(user_hash, sort='rate'):
    user = db.User(user_hash)
    user_best = user.load_best()
    user_info = user.load_user()
    if user_best and user_info:
        return render_template('main.html')
