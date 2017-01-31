#!/usr/bin/env python3
import sqlite3,hashlib,os,json
from pprint import pprint

if __name__ == '__main__':

  con = sqlite3.connect('CHUNITHM-Rate-Calculator.db')
  cur = con.cursor()
  cur.execute('SELECT * FROM User;')
  rows = cur.fetchall()

  for row in rows:
    FriendCode = row[1]
    Json = json.loads(row[3])
    Rate = Json['Date']

    Hash = hashlib.sha256(str(FriendCode).encode('utf8')).hexdigest()
    Path = '../user/{}.db'.format(Hash)
    print(Path)

    if os.path.exists(Path):
      con = sqlite3.connect(Path)
      cur = con.cursor()
    else:
      con = sqlite3.connect(Path)
      cur = con.cursor()
      #新規ユーザーなのでテーブルを作成
      cur.execute('''
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
      cur.execute('''
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
      cur.execute('''
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
      cur.execute('''
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
    
    sql = 'INSERT INTO Rate (DispRate,HighestRating,MaxRate,BestRate,RecentRate,Credits,ExecuteDate) VALUES (?,?,?,?,?,?,?)'
    for i in range(len(Rate['date'])):
      cur.execute(sql,(Rate['DispRate'][i],None,Rate['MaxRate'][i],Rate['BestRate'][i],Rate['RecentRate'][i],Rate['date'][i],None))
      con.commit()
    