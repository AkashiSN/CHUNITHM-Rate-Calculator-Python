#!/usr/bin/env python3
from flask import *
from common import Function as Func
from admin import admin as Admin
import chunithm,os,math,hashlib,sha3

app = Flask(__name__)
# cookieを暗号化する秘密鍵
app.config['SECRET_KEY'] = os.urandom(64)

#エラーハンドラー
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

#----以下ルーティング----

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

@app.route('/chunithm/user/<Hash>')
@app.route('/chunithm/user/<Hash>/best')
@app.route('/chunithm/user/<Hash>/best/<Sort>')
def Best(Hash,Sort='rate'):
    try:
        if Sort == 'rate':
            Best, User, Rate = chunithm.DispBest(Hash)
            return render_template(
                'Main.html',
                Hash=Hash,
                frame='Best',
                Musics=Best,
                User=User[-1],
                Rate=Rate
            )
        elif Sort == 'score':
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
        elif Sort == 'difficult':
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

    except Exception as e:
        return render_template(
            'Main.html',
            frame='Error',
            url='/',
            Message='ユーザーが登録されていません。'
        )

@app.route('/chunithm/user/<Hash>/recent')
def Recent(Hash):
    try:
        Recent, User, Rate = chunithm.DispRecent(Hash)
        return render_template(
            'Main.html',
            Hash=Hash,
            frame='Recent',
            Musics=Recent,
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

@app.route('/chunithm/user/<Hash>/graph')
def Graph(Hash):
    try:
        User, Rate = chunithm.DispGraph(Hash)
        return render_template(
            'Main.html',
            Hash=Hash,
            frame='Graph',
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

@app.route('/chunithm/user/<Hash>/tools', methods=['POST', 'GET'])
def Tools(Hash):
    User, Rate = chunithm.DispTools(Hash)

    if User is None or Rate is None:
        return render_template(
            'Main.html',
            frame='Error',
            url='/',
            Message='ユーザーが登録されていません。'
        )
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

#-----------以下管理ページ------------

app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'd5278e5502686c56f86b6e5c8eacc0820690da1177822df26d286bac257173e1296af399794f7bcb0237feca9c68b9e5d705ae675287f619143049874ca74505'

@app.route('/admin', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['UserName'] == app.config['USERNAME']:
            if hashlib.sha3_512(str(request.form['Password']).encode('utf8')).hexdigest() == app.config['PASSWORD']:
                session['logged_in'] = True
                return redirect('/admin/home/overview')
        return render_template(
            'Login.html',
            Error='Invalid UserName or Password'
        )
    else:
        return render_template(
            'Login.html'
        )



@app.route('/admin/home')
@app.route('/admin/home/<frame>')
def admin(frame='overview'):
    if 'logged_in' in session and session['logged_in'] is True:
        admin_connect = Admin.AdminDataBase()
        users = admin_connect.LoadData()
        Number_of_Users = len(users)
        users = sorted(users,key=lambda x:x["HighestRating"],reverse=True)

        return render_template(
            'Admin.html',
            page='Home',
            frame=frame,
            Number_of_Users=Number_of_Users,
            Users=users[0:10],
        )
    else:
        return redirect('/admin')

@app.route('/admin/user',methods=['GET','POST'])
def user():
    if 'logged_in' in session and session['logged_in'] is True:
        admin_connect = Admin.AdminDataBase()
        if request.method == 'POST':
            Dic = {
                'UserName':request.form['UserName'],
                'FriendCode':request.form['FriendCode'],
                'Credits':request.form['Credits'],
                'DispRate':request.form['DispRate'],
                'HighestRating':request.form['HighestRating'],
                'MaxRate':request.form['MaxRate'],
                'BestRate':request.form['BestRate'],
                'RecentRate':request.form['RecentRate']
            }
            users = admin_connect.SerchUser(Dic)
        else:
            Dic = {}
            users = admin_connect.LoadData()
        Number_of_Users = len(users)
        users = sorted(users,key=lambda x:x["HighestRating"],reverse=True)
        return render_template(
            'Admin.html',
            page='Users',
            Number_of_Users=Number_of_Users,
            Users=users,
            Dic=Dic
        )
    else:
        return redirect('/admin')

@app.route('/admin/music', methods=['POST', 'GET'])
@app.route('/admin/music/<frame>', methods=['POST', 'GET'])
def music(frame='all'):
    f = open(os.path.dirname(__file__)+"/pass.json", 'r',encoding='utf8')
    data = json.load(f)
    userId = Func.Get_userId(data['user'],data['pass'])
    if request.method == 'POST':
        if float(request.form['BaseRate']) > 0:
            if 'logged_in' in session and session['logged_in'] is True:
                MusicId = request.form['MusicId']
                Level = request.form['Level']
                BaseRate = request.form['BaseRate']
                chunithm.SetMusic(userId,MusicId,Level,BaseRate)
        else:
            Dic = {
                'MusicName':request.form['MusicName'],
                'DiffLevel':request.form['DiffLevel'],
                'Level':request.form['Level'],
                'Genre':request.form['Genre']
            }
            MusicList = chunithm.SearchMusic(userId,Dic)
            DiffLevel = {
                '2':'Expert',
                '3':'Master',
                '':'難易度'
            }
            Genre = {
                '99':'全ジャンル',
                '00':'POPS &amp; ANIME',
                '01':'GAME',
                '02':'niconico',
                '03':'東方Project',
                '05':'ORIGINAL',
                '06':'VARIETY',
                '07':'イロドリミドリ',
                '08':'言ノ葉Project'
            }
            tmp = {
                'name':DiffLevel[Dic['DiffLevel']],
                'value':Dic['DiffLevel']
            }
            Dic['DiffLevel'] = tmp 
            tmp = {
                'name':Genre[Dic['Genre']],
                'value':Dic['Genre']
            }
            Dic['Genre'] = tmp
            MusicList = sorted(MusicList,key=lambda x:x["MusicId"])
            return render_template(
                'Admin.html',
                page='Music',
                MusicList=MusicList,
                Name='検索結果',
                Dic=Dic,
                frame=frame
            )
    NoneMusicList,ExistMusicList = chunithm.CheckMusic(userId)
    if frame == 'all':
        MusicList = NoneMusicList + ExistMusicList
        MusicList = sorted(MusicList,key=lambda x:x["MusicId"])
    elif frame == 'unregistered':
        MusicList = sorted(NoneMusicList,key=lambda x:x["MusicId"])
    elif frame == 'registered':
        MusicList = sorted(ExistMusicList,key=lambda x:x["MusicId"])
    Dic = {}
    name = {'all':'全楽曲一覧','unregistered':'未登録楽曲一覧','registered':'登録楽曲一覧'}
    return render_template(
        'Admin.html',
        page='Music',
        MusicList=MusicList,
        Name=name[frame],
        Dic=Dic,
        frame=frame
    )

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/admin')

@app.route('/debug', methods=['POST'])
def debug():
    if request.method == 'POST':
        userId = Func.userId_Get(request.form['userid'])
        return userId

if __name__ == '__main__':
  app.run('0.0.0.0',5555,debug=True)