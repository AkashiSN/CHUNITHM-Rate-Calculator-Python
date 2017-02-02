#!/usr/bin/env python3
from flask import *
import flask_login
from common import Function as Func
import chunithm,os,math,hashlib

app = Flask(__name__)
# cookieを暗号化する秘密鍵
app.config['SECRET_KEY'] = os.urandom(64)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chunithm.php', methods=['POST', 'GET'])
def old_page():
    return render_template(
        'Main.html',
        frame='Error',
        url='/',
        Message='コードが更新されましたので、新しいコードを登録してから実行してください。'
    )


@app.route('/chunithm.api', methods=['POST', 'GET'])
def Chunithm():
    if request.method == 'POST':
        userId = Func.userId_Get(request.form['userid'])
        if userId is None:
            return render_template(
                'Main.html',
                frame='Error',
                Message='送信されたデータにはUserIDが含まれていません。CHUNITHM-NETにログインして実行してください。'
            )
        Hash = chunithm.CalcRate(userId)
        if Hash is None:
            return render_template(
                'Main.html',
                frame='Error',
                Message='このUserIdは無効です。もう一度CHUNITHM-NETにログインして実行してください。'
            )
        return redirect('/chunithm/user/' + Hash)
    else:
        return render_template(
            'Main.html',
            frame='Error',
            url='/',
            Message='許可されてないアクセスです。'
        )

@app.errorhandler(404)
def page_not_found(e):
    return render_template( 
        'Main.html',
        frame='Error',
        url='/',
        Message='-404-\n目的のページが見つかりません。'
    )

@app.errorhandler(405)
def page_not_found(e):
    return render_template( 
        'Main.html',
        frame='Error',
        url='/',
        Message='-405-\n許可されてないアクセスです。'
    )

@app.errorhandler(500)
def page_not_found(e):
    return render_template( 
        'Main.html',
        frame='Error',
        url='/',
        Message='内部でエラーが発生しました。'
    )

@app.route('/chunithm/user/<Hash>')
@app.route('/chunithm/user/<Hash>/best')
@app.route('/chunithm/user/<Hash>/best/rate')
def Best(Hash):
    try:
        Best, User, Rate = chunithm.DispBest(Hash)

        return render_template(
            'Main.html',
            Hash=Hash,
            frame='Best',
            Musics=Best,
            User=User[-1],
            Rate=Rate
        )     
    except Exception as e:
        return render_template( 
            'Main.html',
            frame='Error',
            url='/',
            Message='ユーザーが登録されていません。'
        )

@app.route('/chunithm/user/<Hash>/best/score')
def Best_Score(Hash):
    Best, User, Rate = chunithm.DispBest(Hash)
    Best = sorted(Best, key=lambda x: x['Score'], reverse=True)
    Best = Func.CountRank(Best)
    return render_template(
        'Main.html',
        Hash=Hash,
        frame='Best',
        Musics=Best,
        User=User[-1],
        Rate=Rate,
        Sort='score',
    )

@app.route('/chunithm/user/<Hash>/best/difficult')
def Best_Difficult(Hash):
    Best, User, Rate = chunithm.DispBest(Hash)
    Best = sorted(Best, key=lambda x: x['BaseRate'], reverse=True)
    Best = Func.CountDiff(Best)
    return render_template(
        'Main.html',
        Hash=Hash,
        frame='Best',
        Musics=Best,
        User=User[-1],
        Rate=Rate,
        Sort='difficult'
    )

@app.route('/chunithm/user/<Hash>/recent')
def Recent(Hash):
    Recent, User, Rate = chunithm.DispRecent(Hash)
    return render_template(
        'Main.html',
        Hash=Hash,
        frame='Recent',
        Musics=Recent,
        User=User[-1],
        Rate=Rate
    )

@app.route('/chunithm/user/<Hash>/graph')
def Graph(Hash):
    User, Rate = chunithm.DispGraph(Hash)
    return render_template(
        'Main.html',
        Hash=Hash,
        frame='Graph',
        User=User[-1],
        Rate=Rate
    )

@app.route('/chunithm/user/<Hash>/tools', methods=['POST', 'GET'])
def Tools(Hash):
    User, Rate = chunithm.DispTools(Hash) 
    BaseRate = ''
    Score = ''
    MaxRate = ''

    if request.method == 'POST':
        try:
            BaseRate = float(request.form['baserate'])
            Score = int(request.form['score'])
            PreRecent = Func.Score2Rate(Score,BaseRate)
            MaxRate = math.floor(((Rate[-1]['BestRate'] * 30 + PreRecent * 10) / 40) * 100) / 100
        except Exception as e:
            return render_template(
                'Main.html',
                Hash=Hash,
                frame='Tools',
                User=User[-1],
                Rate=Rate
            )
        
    return render_template(
        'Main.html',
        Hash=Hash,
        frame='Tools',
        User=User[-1],
        Rate=Rate,
        BaseRate=BaseRate,
        Score=Score,
        MaxRate=MaxRate
    )

users = {'admin': {'pw': 'f3ff072775528827927e82173d3c78e1f7c79a11b8ec1056c125597156c37e0d728044c71258e27a827b784b2e4ee734e60d871b7ea046f7b8b8ee371f507edc'}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(ID):
    if ID not in users:
        return

    user = User()
    user.id = ID
    return user

@login_manager.request_loader
def request_loader(request):
    ID = request.form.get('id')
    if ID not in users:
        return

    user = User()
    user.id = ID
    
    Hash = hashlib.sha256(request.form['pw'].encode('utf8')).hexdigest()

    user.is_authenticated = Hash == users[ID]['pw']

    return user

@app.route('/admin', methods=['POST', 'GET'])
def Admin():
    if request.method == 'POST':
        ID = request.form['id']
        if flask.request.form['pw'] == users[ID]['pw']:
            user = User()
            user.id = ID
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('protected'))
        return 'Bad login'

    else:
        return render_template(
            'Admin.html'
        )

@app.route('/admin/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/admin/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

# @app.route('/admin/login')
# def Login():
#      # ログイン処理
#     if request.method == 'POST' and _is_account_valid():
#         # セッションにユーザ名を保存してからトップページにリダイレクト
#         session['username'] = request.form['username']
#         return redirect(url_for('index'))
#     # ログインページに戻る
#     return render_template('login.html')


# # 個人認証を行い，正規のアカウントか確認する
# def _is_account_valid():  
#     username = request.form.get('username')
#     # この例では，ユーザ名にadminが指定されていれば正規のアカウントであるとみなしている
#     # ここで具体的な個人認証処理を行う．認証に成功であればTrueを返すようにする
#     if username == 'admin':
#         return True
#     return False