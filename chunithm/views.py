from chunithm import app
from chunithm import db
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
from chunithm.forms import LoginForm
from chunithm.models import User
from chunithm import func
from chunithm import db
from chunithm import chunithm

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('secure_page'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next = request.args.get('next')
            return redirect(url_for('secure_page'))
        else:
            flash('Username or Password is incorrect.', 'danger')
    flash_errors(form)
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('home'))

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the {} field - {}".format (getattr(form, field).label.text, error), 'danger')


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
