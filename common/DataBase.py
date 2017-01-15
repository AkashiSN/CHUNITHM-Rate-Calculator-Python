# -*- coding: utf-8 -*-
#! python3
import sqlite3,os
from common import Function as Func
from pprint import pprint

#譜面定数取得
class LoadBaseRate:
  '''譜面定数をデータベースから取得する'''
  #前処理
  def __init__(self):
    self.con = sqlite3.connect("common/chunithm.db")
    self.cur = self.con.cursor()

  #譜面定数を取得する
  def Get_BaseRate(self,musicId,level):
    sql = 'SELECT * FROM Music WHERE "MusicId" = ? AND "Level" = ?'
    self.cur.execute(sql,(musicId,level))
    row = self.cur.fetchone()
    if row is None:
      return None
    BaseRate = {
      'MusicId':row[0],
      'Level':row[1],
      'MusicName':row[2],
      'Image':row[3],
      'BaseRate':row[4],
      'Air':row[5]
    }
    return BaseRate

  #ファイル名からMusicIdを取得
  def Get_MusicId(self,FileName):
    sql = 'SELECT * FROM Music WHERE "Image" = ?'
    self.cur.execute(sql,(FileName,))
    r = self.cur.fetchone()
    return r[0]

#各ユーザのデーターベース
class UserDataBase:
  '''各ユーザーのデータベースに計算結果を保存する'''
  #前処理
  def __init__(self,Hash):
    Path = 'user/{}.db'.format(Hash)
    #新規ユーザーかどうか
    if os.path.exists(Path):
      self.con = sqlite3.connect(Path)
      self.cur = self.con.cursor()
    else:
      self.con = sqlite3.connect(Path)
      self.cur = self.con.cursor()
      #新規ユーザーなのでテーブルを作成
      self.cur.execute('''
        CREATE TABLE `Best` (
          `MusicId` INTEGER,
          `Level` INTEGER,
          `MusicName` TEXT,
          `Image` TEXT,
          `BaseRate`  INTEGER,
          `Score` INTEGER,
          `MaxScore`  INTEGER,
          `Rate`  INTEGER
        );
      ''')
      self.cur.execute('''
        CREATE TABLE `Rate` (
          `DispRate`  INTEGER,
          `HighestRating` INTEGER,
          `MaxRate` INTEGER,
          `BestRate`  INTEGER,
          `RecentRate`  INTEGER,
          `Credits` INTEGER,
          `ExecuteDate` TEXT
        );
      ''')
      self.cur.execute('''
        CREATE TABLE `Recent` (
          `MusicId` INTEGER,
          `Level` INTEGER,
          `MusicName` TEXT,
          `Image` TEXT,
          `BaseRate`  INTEGER,
          `Score` INTEGER,
          `Rate`  INTEGER,
          `PlayDate` TEXT
        );
      ''')
      self.cur.execute('''
        CREATE TABLE `User` (
          'Id'  INTEGER,
          `UserName`  TEXT,
          `Level` INTEGER,
          `TotalPoint`  INTEGER,
          `TrophyType`  INTEGER,
          `WebLimitDate`  TEXT,
          `CharacterFileName` TEXT,
          `FriendCount` INTEGER,
          `Point` INTEGER,
          `PlayCount` INTEGER,
          `CharacterLevel`  INTEGER,
          `TrophyName`  TEXT,
          `ReincarnationNum`  INTEGER,
          `FriendCode`  INTEGER,
          `Hash`  TEXT,
          `FinalPlayDate` TEXT,
          `ExecuteDate` TEXT,
          PRIMARY KEY(`Id`)
        );
      ''')

  #ベスト枠を保存する
  def SetBest(self,Best):
    #一度削除してからセットする
    self.cur.execute('DELETE FROM Best')
    sql = 'INSERT INTO Best (MusicId,Level,MusicName,Image,BaseRate,Score,MaxScore,Rate) VALUES (?,?,?,?,?,?,?,?)'
    for Music in Best:
      self.cur.execute(sql,(Music['MusicId'],Music['Level'],Music['MusicName'],Music['Image'],Music['BaseRate'],Music['Score'],Music['MaxScore'],Music['Rate']))
      self.con.commit()

  #リセント候補枠を保存する
  def SetRecent(self,Recent):
    #一度削除してからを保存する
    self.cur.execute('DELETE FROM Recent')
    sql = 'INSERT INTO Recent (MusicId,Level,MusicName,Image,BaseRate,Score,Rate,PlayDate) VALUES (?,?,?,?,?,?,?,?)'
    for Music in Recent:
      self.cur.execute(sql,(Music['MusicId'],Music['Level'],Music['MusicName'],Music['Image'],Music['BaseRate'],Music['Score'],Music['Rate'],Music['PlayDate']))
      self.con.commit()

  #ユーザー情報を保存する
  def SetUser(self,User):
    sql = 'SELECT * FROM User WHERE PlayCount = ?'
    self.cur.execute(sql,(User['PlayCount'],))
    r = self.cur.fetchall()
    if r:
      sql = 'DELETE FROM User WHERE PlayCount = ?'
      self.cur.execute(sql,(User['PlayCount'],))
    sql = 'INSERT INTO User (UserName,Level,TotalPoint,TrophyType,WebLimitDate,characterFileName,FriendCount,`Point`,PlayCount,CharacterLevel,TrophyName,ReincarnationNum,FriendCode,Hash,FinalPlayDate,ExecuteDate) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    self.cur.execute(sql,(User['UserName'],User['Level'],User['TotalPoint'],User['TrophyType'],User['WebLimitDate'],User['CharacterFileName'],User['FriendCount'],User['Point'],User['PlayCount'],User['CharacterLevel'],User['TrophyName'],User['ReincarnationNum'],User['FriendCode'],User['Hash'],User['FinalPlayDate'],User['ExecuteDate']))
    self.con.commit()

  #レートの推移を保存する
  def SetRate(self,Rate):
    sql = 'SELECT * FROM Rate WHERE Credits = ?'
    self.cur.execute(sql,(Rate['Credits'],))
    r = self.cur.fetchall()
    if r:
      sql = 'DELETE FROM Rate WHERE Credits = ?'
      self.cur.execute(sql,(Rate['Credits'],))
    sql = 'INSERT INTO Rate (DispRate,HighestRating,MaxRate,BestRate,RecentRate,Credits,ExecuteDate) VALUES (?,?,?,?,?,?,?)'
    self.cur.execute(sql,(Rate['DispRate'],Rate['HighestRating'],Rate['MaxRate'],Rate['BestRate'],Rate['RecentRate'],Rate['Credits'],Rate['ExecuteDate']))
    self.con.commit()

  #ベスト枠を読み込む
  def LoadBest(self):
    self.cur.execute("SELECT * FROM Best")
    rows = self.cur.fetchall()
    if rows:
      Best = []
      dif = {3:'master',2:'expert'}
      for row in rows:
        Dic = {
          'MusicId':row[0],
          'Level':row[1],
          'MusicName':row[2],
          'Image':row[3],
          'BaseRate':row[4],
          'Score':row[5],
          'MaxScore':row[6],
          'Rate':row[7],
          'Rank':Func.Score2Rank(row[5]),
          'LevelName':dif[row[1]],
          'Diff':Func.BaseRate2Diff(row[4])
        }
        Best.append(Dic)
      return Best
    else:
      return None

  #リセント候補枠を読み込む
  def LoadRecent(self):
    self.cur.execute("SELECT * FROM Recent")
    rows = self.cur.fetchall()
    if rows:
      Recent = []
      dif = {3:'master',2:'expert'}
      for row in rows:
        Dic = {
          'MusicId':row[0],
          'Level':row[1],
          'MusicName':row[2],
          'Image':row[3],
          'BaseRate':row[4],
          'Score':row[5],
          'Rate':row[6],
          'PlayDate':row[7],
          'Rank':Func.Score2Rank(row[5]),
          'LevelName':dif[row[1]]
        }
        Recent.append(Dic)
      return Recent
    else:
      return None

  #ユーザーデータを読み込む
  def LoadUser(self):
    self.cur.execute('SELECT * FROM User')
    rows = self.cur.fetchall()
    if rows:
      User = []
      characterFrame = ['normal', 'copper', 'silver', 'gold', 'gold', 'platina']
      for row in rows:
        Dic = {
          'Id':row[0],
          'UserName':row[1],
          'Level':row[2],
          'TotalPoint':row[3],
          'TrophyType':row[4],
          'WebLimitDate':row[5],
          'CharacterFileName':row[6],
          'FriendCount':row[7],
          'Point':row[8],
          'PlayCount':row[9],
          'CharacterLevel':row[10],
          'TrophyName':row[11],
          'ReincarnationNum':row[12],
          'FriendCode':row[13],
          'Hash':row[14],
          'FinalPlayDate':row[15],
          'ExecuteDate':row[16],
          'CharacterFrameFile':characterFrame[int(row[10]/5)],
          'Honor':characterFrame[row[4]]
        }
        User.append(Dic)
      return User
    else:
      return  None

  #レートの推移を読み込む
  def LoadRate(self):
    self.cur.execute('SELECT * FROM Rate')
    rows = self.cur.fetchall()
    if rows:
      Rate = []
      for row in rows:
        Dic = {
          'DispRate':row[0],
          'HighestRating':row[1],
          'MaxRate':row[2],
          'BestRate':row[3],
          'RecentRate':row[4],
          'Credits':row[5],
          'ExecuteDate':row[6]
        }
        Rate.append(Dic)
      return Rate
    else:
      return None

#管理用のデータベース
class AdminDataBase():
  '''管理用のデータベース'''
  def __init__(self):
    if os.path.exists('admin/admin.db'):
      self.con = sqlite3.connect('admin/admin.db')
      self.cur = self.con.cursor()
    else:
      self.con = sqlite3.connect('admin/admin.db')
      self.cur = self.con.cursor()
      self.cur.execute('''
        CREATE TABLE `User` (
          `UserName`  TEXT,
          `FriendCode`  TEXT,
          `Hash`  TEXT,
          `Credits` INTEGER,
          `DispRate`  INTEGER,
          `HighestRating` INTEGER,
          `MaxRate` INTEGER,
          `BestRate`  INTEGER,
          `RecentRate`  INTEGER
        );
      ''')

  #データを保存する
  def SetData(self,Data):
    sql = 'SELECT * FROM User WHERE Hash = ?'
    self.cur.execute(sql,(Data['Hash'],))
    r = self.cur.fetchall()
    if r:
      sql = 'DELETE FROM User WHERE Hash = ?'
      self.cur.execute(sql,(Data['Hash'],))
    sql = 'INSERT INTO User (UserName,FriendCode,Hash,Credits,DispRate,HighestRating,MaxRate,BestRate,RecentRate) VALUES (?,?,?,?,?,?,?,?,?)'
    self.cur.execute(sql,(Data['UserName'],Data['FriendCode'],Data['Hash'],Data['Credits'],Data['DispRate'],Data['HighestRating'],Data['MaxRate'],Data['BestRate'],Data['RecentRate']))
    self.con.commit()