#!/usr/bin/env python3
from flask import *
from common import Function as Func
from admin import admin as Admin
import chunithm,os,math,hashlib,sha3

app = Flask(__name__)
# cookieを暗号化する秘密鍵
app.config['SECRET_KEY'] = os.urandom(64)

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

@app.route('/admin')
def admin():
  if 'logged_in' in session and session['logged_in'] is True:
    admin_connect = Admin.AdminDataBase()
    users = admin_connect.LoadData()
    User_count = len(users)
    users = sorted(users,key=lambda x:x["HighestRating"],reverse=True)

    return render_template(
      'Admin.html',
      authenticated=True,
      count=User_count,
      User=users[0:10],
    )
  else:
    return redirect('/admin/login')

app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'd5278e5502686c56f86b6e5c8eacc0820690da1177822df26d286bac257173e1296af399794f7bcb0237feca9c68b9e5d705ae675287f619143049874ca74505'

@app.route('/admin/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif hashlib.sha3_512(str(request.form['password']).encode('utf8')).hexdigest() != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect('/admin')
    return render_template(
        'Admin.html', 
        Error=error
    )

@app.route('/admin/user')
def user():
    if 'logged_in' in session and session['logged_in'] is True:
        admin_connect = Admin.AdminDataBase()
        users = admin_connect.LoadData()
        User_count = len(users)
        users = sorted(users,key=lambda x:x["HighestRating"],reverse=True)
        return render_template(
            'Admin.html',
            frame='user',
            authenticated=True,
            count=User_count,
            User=users,
        )
    else:
        return redirect('/admin/login')

@app.route('/admin/music', methods=['GET','POST'])
def music():
    if 'logged_in' in session and session['logged_in'] is True:
        f = open(os.path.dirname(__file__)+"/pass.json", 'r',encoding='utf8')
        data = json.load(f)
        userId = Func.Get_userId(data['user'],data['pass'])
        if request.method == 'POST':
            MusicId = request.form['MusicId']
            Level = request.form['Level']
            BaseRate = request.form['BaseRate']
            chunithm.SetMusic(userId,MusicId,Level,BaseRate)
            NoneMusicList,ExistMusicList = chunithm.CheckMusic(userId)
            return render_template(
                'Admin.html',
                frame='music',
                authenticated=True,
                NoneMusicList=NoneMusicList,
                ExistMusicList=ExistMusicList
            )
        else:
            NoneMusicList,ExistMusicList = chunithm.CheckMusic(userId)
            return render_template(
                'Admin.html',
                frame='music',
                authenticated=True,
                NoneMusicList=NoneMusicList,
                ExistMusicList=ExistMusicList
            )
    else:
        return redirect('/admin/login')

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('admin', None)
    flash('You were logged out')
    return redirect('/admin/login')
