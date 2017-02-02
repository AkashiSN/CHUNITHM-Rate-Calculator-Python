#!/usr/bin/env python3
from flask import *
import flask_login
from common import Function as Func
import chunithm,os,math,hashlib,sha3

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

users = {'admin': {'pw': '46df5dbdce3ce58b5eac31d0723b8746c981fef6021c9a57cc3df313256b4eed815281b26802c0db2c30c478eabdb72544d1596602731b4f25224ae73516b396'}}

class User(flask_login.UserMixin):
  is_authenticated = False

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

  Hash = hashlib.sha3_512(str(request.form['password']).encode('utf8')).hexdigest()

  user.is_authenticated = Hash == users[ID]['pw']

  return user



@app.route('/admin')
@flask_login.login_required
def Admin():
  return render_template(
    'Admin.html',
    authenticated=flask_login.current_user.is_authenticated
  )
    
@login_manager.unauthorized_handler
def unauthorized_handler():
  return redirect('/admin/login')


@app.route('/admin/login', methods=['POST','GET'])
def login():
  if flask_login.current_user.is_authenticated:
    return redirect('/admin')
  if request.method == 'POST':
      ID = request.form['id']
      Hash = hashlib.sha3_512(request.form['password'].encode('utf8')).hexdigest()
        
      if Hash == users[ID]['pw']:
        user = User()
        user.id = ID
        flask_login.login_user(user)
        return redirect('/admin')
      else:
        return render_template(
          'Admin.html',
          Error=' ログインに失敗しました。'
        )
  else:
    return render_template(
     'Admin.html'
    )    

@app.route('/admin/logout')
def logout():
    flask_login.logout_user()
    return redirect('/admin/login')

