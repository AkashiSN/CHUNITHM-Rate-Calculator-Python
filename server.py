#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for
from common import Function as Func
import chunithm
import os

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
  return render_template('index.html')
  
@app.route('/chunithm',methods=['POST', 'GET'])
def Chunithm():
  if request.method == 'POST':
    userId = Func.userId_Get(request.form['userid'])
    Hash = chunithm.CalcRate(userId)
    return redirect('/chunithm/user/' + Hash)
  else:
    return "a"

@app.route('/chunithm/user/<Hash>')
@app.route('/chunithm/user/<Hash>/best')
@app.route('/chunithm/user/<Hash>/best/rate')
def Best(Hash):
  Best,User,Rate = chunithm.DispBest(Hash)
  return render_template(
    'Main.html',
    Hash=Hash,
    frame="Best",
    Musics=Best,
    User=User[0],
    Rate=Rate[0]
  )

@app.route('/chunithm/user/<Hash>/best/score')
def Best_Score(Hash):
  Best,User,Rate = chunithm.DispBest(Hash)
  Best = sorted(Best,key=lambda x:x["Score"],reverse=True)
  Best = Func.CountRank(Best)
  return render_template(
    'Main.html',
    Hash=Hash,
    frame="Best",
    Musics=Best,
    User=User[0],
    Rate=Rate[0],
    Sort='score',
  )

@app.route('/chunithm/user/<Hash>/best/difficult')
def Best_Difficult(Hash):
  Best,User,Rate = chunithm.DispBest(Hash)
  Best = sorted(Best,key=lambda x:x["BaseRate"],reverse=True)
  Best = Func.CountDiff(Best)
  return render_template(
    'Main.html',
    Hash=Hash,
    frame="Best",
    Musics=Best,
    User=User[0],
    Rate=Rate[0],
    Sort='difficult'
  )
  
@app.route('/chunithm/user/<Hash>/recent')
def Recent(Hash):
  Recent,User,Rate = chunithm.DispRecent(Hash)
  return render_template(
    'Main.html',
    Hash=Hash,
    frame="Recent",
    Musics=Recent,
    User=User[0],
    Rate=Rate[0]
  )

@app.route('/chunithm/user/<Hash>/graph')
def Graph(Hash):
  User,Rate = chunithm.DispGraph(Hash)
  return render_template(
    'Main.html',
    Hash=Hash,
    frame="Graph",
    User=User[0],
    Rate=Rate[0]
  )

if __name__ == '__main__':
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '7777'))
	except ValueError:
		PORT = 5555
	app.run(HOST, PORT)
