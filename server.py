#!/usr/bin/env python3
from flask import *
from common import Function as Func
import chunithm,os,math

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chunithm.api', methods=['POST', 'GET'])
def Chunithm():
    if request.method == 'POST':
        userId = Func.userId_Get(request.form['userid'])
        try:
            Hash = chunithm.CalcRate(userId)
            return redirect('/chunithm/user/' + Hash)
        except Exception as e:
            return render_template(
                'Main.html',
                frame='Error',
                Message='このUserIdは無効です。もう一度CHUNITHM-NETにログインして実行してください。'
            )
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
        Message='-404-<br>目的のページが見つかりません。'
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
        BaseRate = float(request.form['baserate'])
        Score = int(request.form['score'])
        PreRecent = Func.Score2Rate(Score,BaseRate)
        MaxRate = math.floor(((Rate[-1]['BestRate'] * 30 + PreRecent * 10) / 40) * 100) / 100

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
def Admin():
    return render_template(
        'Admin.html'
    )