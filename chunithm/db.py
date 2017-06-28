# -*- coding: utf-8 -*-
#! python3
import sqlite3
import os
# from chunithm import func


class music_base_rate:
    '''楽曲のデータベース'''

    def __init__(self):
        '''事前処理'''
        path = os.path.dirname(__file__)+'/db/chunithm.db'
        if os.path.exists(path):
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
        else:
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
            self.cur.execute('''
                CREATE TABLE `music` (
                  `music_id` INTEGER,
                  `music_name` TEXT,
                  `music_cover_image` TEXT,
                  `music_artist_name` TEXT,
                  `music_difficulty`  INTEGER,
                  `music_level` INTEGER,
                  `music_base_rate`  INTEGER
                );
              ''')

    def fetch_music_info_rom_music_id_music_difficulty(self, music_id, music_difficulty):
        '''楽曲idと楽曲の難易度から曲の情報をフェッチし返す'''
        sql = 'SELECT * FROM music WHERE "music_id" = ? AND "music_difficulty" = ?'
        self.cur.execute(sql, (music_id, music_difficulty))
        row = self.cur.fetchone()
        if row is None:
            return None
        music = {
            'music_id': row[0],
            'music_name': row[1],
            'music_cover_image': row[2],
            'music_artist_name': row[3],
            'music_difficulty': row[4],
            'music_level': row[5],
            'music_base_rate': row[6]
        }
        return music

    def fetch_music_list(self):
        '''登録されている楽曲の楽曲idを難易度ごとにフェッチし返す'''
        self.cur.execute('SELECT * FROM music WHERE "music_difficulty" = 2')
        rows = self.cur.fetchall()
        if rows:
            expert_music_base_rate = []
            for row in rows:
                expert_music_base_rate.append(row[0])
        else:
            expert_music_base_rate = None

        self.cur.execute('SELECT * FROM music WHERE "music_difficulty" = 3')
        rows = self.cur.fetchall()
        if rows:
            music_base_rate = []
            for row in rows:
                music_base_rate.append(row[0])
        else:
            music_base_rate = None

        return expert_music_base_rate, music_base_rate

    def fetch_music_id_from_file_name(self, file_name):
        '''登録されている楽曲の中からカバーイラストのファイル名から楽曲idをフェッチして返す'''
        sql = 'SELECT * FROM music WHERE "music_cover_image" = ?'
        self.cur.execute(sql,(file_name,))
        r = self.cur.fetchone()
        if r is None:
            return None
        else:
            return r[0]

    def update_music_info(self, music, music_shortage=None):
        '''楽曲情報を更新する'''
        sql = 'SELECT * FROM music WHERE music_id = ? AND music_difficulty = ?'
        self.cur.execute(sql, (music['music_id'], music['music_difficulty']))
        row = self.cur.fetchone()
        if row:
            sql = 'DELETE FROM music WHERE music_id = ? AND music_difficulty = ?'
            self.cur.execute(sql, (music['music_id'], music['music_difficulty']))
        if music_shortage:
            sql = '''
            INSERT INTO music (
                music_id,
                music_name,
                music_cover_image,
                music_artist_name,
                music_difficulty,
                music_level,
                music_base_rate
            ) VALUES (?,?,?,?,?,?,?);'''
            self.cur.execute(
                sql, (
                    music['music_id'],
                    music['music_name'],
                    music['music_cover_image'],
                    music['music_artist_name'],
                    music['music_difficulty'],
                    music['music_level'],
                    music['music_base_rate']
                )
            )
            self.con.commit()
        else:
            sql = '''
            INSERT INTO music (
                music_id,
                music_name,
                music_cover_image,
                music_artist_name,
                music_difficulty,
                music_level,
                music_base_rate
            ) VALUES (?,?,?,?,?,?,?)'''
            self.cur.execute(
                sql, (
                    music['music_id'],
                    music['music_name'],
                    music['music_cover_image'],
                    music['music_artist_name'],
                    music['music_difficulty'],
                    music['music_level'],
                    music['music_base_rate']
                )
            )
            self.con.commit()

    # 楽曲検索
    def serch_music(self, data):
        if data['music_name'] or data['music_difficulty'] or data['music_level']:
            if data['music_name']:
                sql = 'SELECT * FROM music where music_name like ?'
                music_name = '%'+data['music_name']+'%'
                if data['music_level']:
                    sql += ' AND'
            else:
                sql = 'SELECT * FROM music'
                if data['music_level'] or data['music_difficulty']:
                    sql += ' WHERE'

            if data['music_level']:
                if data['music_level'] == '13+':
                    sql += ' music_base_rate between 13.7 and 13.9'
                elif data['music_level'] == '13':
                    sql += ' music_base_rate between 13 and 13.6'
                elif data['music_level'] == '12+':
                    sql += ' music_base_rate between 12.7 and 12.9'
                elif data['music_level'] == '12':
                    sql += ' music_base_rate between 12 and 12.6'
                elif data['music_level'] == '11+':
                    sql += ' music_base_rate between 11.7 and 11.9'
                elif data['music_level'] == '11':
                    sql += ' music_base_rate between 11 and 11.6'
                if data['music_difficulty'] == '2' or data['music_difficulty'] == '3':
                    sql += ' AND'
            if data['music_difficulty']:
                if data['music_difficulty'] == '2':
                    sql += ' music_level = 2'
                elif data['music_difficulty'] == '3':
                    sql += ' music_level = 3'
        else:
            sql = 'SELECT * FROM music'

        if data['music_name']:
            self.cur.execute(sql, (music_name,))
        else:
            self.cur.execute(sql)

        rows = self.cur.fetchall()
        if rows is None:
            return None
        else:
            music = []
            for row in rows:
                Dic = {
                    'music_id': row[0],
                    'music_name': row[1],
                    'music_cover_image': row[2],
                    'music_artist_name': row[3],
                    'music_difficulty': row[4],
                    'music_level': row[5],
                    'music_base_rate': row[6]
                }
                music.append(Dic)
            return music


class user_data_base:
    '''各ユーザーのデータベースに計算結果を保存する'''

    def __init__(self, hash):
        '''事前処理'''
        path = os.path.dirname(__file__)+'/user/'
        
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        path += '{}.db'.format(Hash)

        if os.path.exists(path):
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
        else:
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
            self.cur.execute('''
                CREATE TABLE `best` (
                  `music_id` INTEGER,
                  `music_name` TEXT,
                  `music_cover_image` TEXT,
                  `music_artist_name` TEXT,
                  `music_difficulty`  INTEGER,
                  `music_level` INTEGER,
                  `music_base_rate`  INTEGER,
                  `music_socore_highest`  INTEGER,
                  `music_rate_hightest`  INTEGER,
                );
              ''')
            self.cur.execute('''
                CREATE TABLE `recent` (
                  `music_id` INTEGER,
                  `music_name` TEXT,
                  `music_cover_image` TEXT,
                  `music_artist_name` TEXT,
                  `music_difficulty`  INTEGER,
                  `music_level` INTEGER,
                  `music_base_rate`  INTEGER,
                  `music_socore`  INTEGER,
                  `music_rate`  INTEGER,
                  `music_play_date` TEXT
                );
              ''')
            self.cur.execute('''
                CREATE TABLE `rate` (
                  `rate_disp`  INTEGER,
                  `rate_highest` INTEGER,
                  `rate_best` INTEGER,
                  `rate_recent`  INTEGER,
                  `rate_max`  INTEGER,
                  `credits` INTEGER,
                  `execute_date` TEXT
                );
              ''')            
            self.cur.execute('''
                CREATE TABLE `user` (
                  'Id'  INTEGER,
                  `userName`  TEXT,
                  `music_level` INTEGER,
                  `TotalPoint`  INTEGER,
                  `TrophyType`  INTEGER,
                  `WebLimitDate`  TEXT,
                  `CharacterFileName` TEXT,
                  `FriendCount` INTEGER,
                  `Point` INTEGER,
                  `PlayCount` INTEGER,
                  `Charactermusic_level`  INTEGER,
                  `TrophyName`  TEXT,
                  `ReincarnationNum`  INTEGER,
                  `FriendCode`  INTEGER,
                  `Hash`  TEXT,
                  `FinalPlayDate` TEXT,
                  `ExecuteDate` TEXT,
                  PRIMARY KEY(`Id`)
                );
              ''')

    def update_best(self, best):
        '''ベスト枠を削除してからベスト枠を更新する'''
        self.cur.execute('DELETE FROM best')
        sql = '''
        INSERT INTO best (
            music_id,
            music_name,
            music_cover_image,
            music_artist_name,
            music_difficulty,
            music_level,
            music_base_rate,
            music_socore_highest,
            music_rate_hightest
        ) VALUES (?,?,?,?,?,?,?,?)'''
        for music in best:
            self.cur.execute(
                sql,(
                    music['music_id'],
                    music['music_name'],
                    music['music_cover_image'],
                    music['music_artist_name'],
                    music['music_difficulty'],
                    music['music_level'],
                    music['music_base_rate'],
                    music['music_socore_highest'],
                    music['music_rate_hightest']
                )
            )
            self.con.commit()

    def update_recent(self, recent):
        # 一度削除してからリセント候補枠を保存する
        self.cur.execute('DELETE FROM recent')
        sql = '''
        INSERT INTO recent (
            'music_id',
            'music_name',
            'music_cover_image',
            'music_artist_name',
            'music_difficulty',
            'music_level',
            'music_base_rate',
            'music_socore',
            'music_rate',
            'music_play_date'
        ) VALUES (?,?,?,?,?,?,?,?)'''
        for music in recent:
            self.cur.execute(
                sql,(
                    music['music_id'],
                    music['music_name'],
                    music['music_cover_image'],
                    music['music_artist_name'],
                    music['music_difficulty'],
                    music['music_level'],
                    music['music_base_rate'],
                    music['music_socore'],
                    music['music_rate'],
                    music['music_play_date']
                )
            )
            self.con.commit()

    # ユーザー情報を保存する
    def Setuser(self, user):
        sql = 'SELECT * FROM user WHERE PlayCount = ?'
        self.cur.execute(sql, (user['PlayCount'],))
        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM user WHERE PlayCount = ?'
            self.cur.execute(sql, (user['PlayCount'],))
        sql = '''
        INSERT INTO user (
            userName,
            music_level,
            TotalPoint,
            TrophyType,
            WebLimitDate,
            characterFileName,
            FriendCount,
            `Point`,
            PlayCount,
            Charactermusic_level,
            TrophyName,
            ReincarnationNum,
            FriendCode,
            Hash,
            FinalPlayDate,
            ExecuteDate
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        
        self.cur.execute(sql, (user['userName'], user['music_level'], user['TotalPoint'], user['TrophyType'], user['WebLimitDate'], user['CharacterFileName'], user['FriendCount'], user[
                         'Point'], user['PlayCount'], user['Charactermusic_level'], user['TrophyName'], user['ReincarnationNum'], user['FriendCode'], user['Hash'], user['FinalPlayDate'], user['ExecuteDate']))
        self.con.commit()

    # レートの推移を保存する
    def SetRate(self, Rate):
        sql = 'SELECT * FROM Rate WHERE Credits = ?'
        self.cur.execute(sql, (Rate['Credits'],))
        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM Rate WHERE Credits = ?'
            self.cur.execute(sql, (Rate['Credits'],))
        sql = 'INSERT INTO Rate (DispRate,HighestRating,MaxRate,BestRate,recentRate,Credits,ExecuteDate) VALUES (?,?,?,?,?,?,?)'
        self.cur.execute(sql, (Rate['DispRate'], Rate['HighestRating'], Rate['MaxRate'], Rate[
                         'BestRate'], Rate['recentRate'], Rate['Credits'], Rate['ExecuteDate']))
        self.con.commit()

    # ベスト枠を読み込む
    def LoadBest(self):
        self.cur.execute("SELECT * FROM Best")
        rows = self.cur.fetchall()
        if rows:
            Best = []
            dif = {3: 'master', 2: 'expert'}
            for row in rows:
                Dic = {
                    'music_id': row[0],
                    'music_level': row[1],
                    'music_name': row[2],
                    'musicImage': row[3],
                    'music_base_rate': row[4],
                    'Score': row[5],
                    'MaxScore': row[6],
                    'Rate': row[7],
                    'Rank': func.Score2Rank(row[5]),
                    'music_levelName': dif[row[1]],
                    'Diff': func.music_base_rate2Diff(row[4])
                }
                Best.append(Dic)
            return Best
        else:
            return None

    # リセント候補枠を読み込む
    def Loadrecent(self):
        self.cur.execute("SELECT * FROM recent")
        rows = self.cur.fetchall()
        if rows:
            recent = []
            dif = {3: 'master', 2: 'expert'}
            for row in rows:
                Dic = {
                    'music_id': row[0],
                    'music_level': row[1],
                    'music_name': row[2],
                    'Image': row[3],
                    'music_base_rate': row[4],
                    'Score': row[5],
                    'Rate': row[6],
                    'PlayDate': row[7],
                    'Rank': func.Score2Rank(row[5]),
                    'music_levelName': dif[row[1]]
                }
                recent.append(Dic)
            return recent
        else:
            return None

    # ユーザーデータを読み込む
    def Loaduser(self):
        self.cur.execute('SELECT * FROM user')
        rows = self.cur.fetchall()
        if rows:
            user = []
            characterFrame = ['normal', 'copper',
                              'silver', 'gold', 'gold', 'platina']
            trophyType = ["normal", "copper", "silver", "gold", "platina"]
            for row in rows:
                Dic = {
                    'Id': row[0],
                    'userName': row[1],
                    'music_level': row[2],
                    'TotalPoint': row[3],
                    'TrophyType': row[4],
                    'WebLimitDate': row[5],
                    'CharacterFileName': row[6],
                    'FriendCount': row[7],
                    'Point': row[8],
                    'PlayCount': row[9],
                    'Charactermusic_level': row[10],
                    'TrophyName': row[11],
                    'ReincarnationNum': row[12],
                    'FriendCode': row[13],
                    'Hash': row[14],
                    'FinalPlayDate': row[15],
                    'ExecuteDate': row[16],
                    'CharacterFrameFile': characterFrame[int(row[10]/5)],
                    'Honor': trophyType[row[4]]
                }
                user.append(Dic)
            return user
        else:
            return None

    # レートの推移を読み込む
    def LoadRate(self):
        self.cur.execute('SELECT * FROM Rate')
        rows = self.cur.fetchall()
        if rows:
            Rate = []
            for row in rows:
                Dic = {
                    'DispRate': row[0],
                    'HighestRating': row[1],
                    'MaxRate': row[2],
                    'BestRate': row[3],
                    'recentRate': row[4],
                    'Credits': row[5],
                    'ExecuteDate': row[6]
                }
                Rate.append(Dic)
            return Rate
        else:
            return None

# 管理用のデータベース


# class AdminDataBase():
#     '''管理用のデータベース'''

#     def __init__(self):
#         path = os.path.dirname(__file__)+'/db/admin.db'
#         if os.path.exists(path):
#             self.con = sqlite3.connect(path)
#             self.cur = self.con.cursor()
#         else:
#             self.con = sqlite3.connect(path)
#             self.cur = self.con.cursor()
#             self.cur.execute('''
#         CREATE TABLE `user` (
#           `userName`  TEXT,
#           `FriendCode`  TEXT,
#           `Hash`  TEXT,
#           `Credits` INTEGER,
#           `DispRate`  INTEGER,
#           `HighestRating` INTEGER,
#           `MaxRate` INTEGER,
#           `BestRate`  INTEGER,
#           `recentRate`  INTEGER
#         );
#       ''')

#     # データを保存する
#     def SetData(self, Data):
#         sql = 'SELECT * FROM user WHERE Hash = ?'
#         self.cur.execute(sql, (Data['Hash'],))
#         r = self.cur.fetchall()
#         if r:
#             sql = 'DELETE FROM user WHERE Hash = ?'
#             self.cur.execute(sql, (Data['Hash'],))
#         sql = 'INSERT INTO user (userName,FriendCode,Hash,Credits,DispRate,HighestRating,MaxRate,BestRate,recentRate) VALUES (?,?,?,?,?,?,?,?,?)'
#         self.cur.execute(sql, (Data['userName'], Data['FriendCode'], Data['Hash'], Data['Credits'], Data[
#                          'DispRate'], Data['HighestRating'], Data['MaxRate'], Data['BestRate'], Data['recentRate']))
#         self.con.commit()
