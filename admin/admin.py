#!/usr/bin/env python3
import sqlite3,os,collections

#管理用のデータベース
class AdminDataBase:
  '''管理用のデータベース'''
  def __init__(self):
    Path = os.path.dirname(__file__)+'/admin.db'
    if os.path.exists(Path):
      self.con = sqlite3.connect(Path)
      self.cur = self.con.cursor()
    else:
      self.con = sqlite3.connect(Path)
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
  def LoadData(self):
    self.cur.execute('SELECT * FROM User')
    rows = self.cur.fetchall()
    if rows:
      user = []
      for row in rows:
        Dic = {
          'UserName':row[0],
          'FriendCode':row[1],
          'Hash':row[2],
          'Credits':row[3],
          'DispRate':row[4],
          'HighestRating':row[5],
          'MaxRate':row[6],
          'BestRate':row[7],
          'RecentRate':row[8]
        }
        user.append(Dic)
      return user
    else:
      return None

  def CountRate(self):
    self.cur.execute('SELECT * FROM User')
    rows = self.cur.fetchall()
    if rows:
      DispRate = []
      HighestRating = []
      MaxRate = []
      BestRate = []
      RecentRate = []
      for row in rows:
        DispRate.append(row[4])
        HighestRating.append(row[5])
        MaxRate.append(row[6])
        BestRate.append(row[7])
        RecentRate.append(row[8])

      DispRate_count = collections.Counter(DispRate)
      HighestRating_count = collections.Counter(HighestRating)
      MaxRate_count = collections.Counter(MaxRate)
      BestRate_count = collections.Counter(BestRate)
      RecentRate_count = collections.Counter(RecentRate)

      return DispRate_count,HighestRating_count,MaxRate_count,MaxRate_count,BestRate_count,RecentRate_count