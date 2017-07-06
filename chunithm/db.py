#!/usr/bin/env python3

import sqlite3
import os
from chunithm import func


class Music:
    """
    楽曲のデータベース
    """

    def __init__(self):
        """
        事前処理
        """
        path = os.path.dirname(__file__)+'/database/chunithm.db'
        if os.path.exists(path):
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
        else:
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
            self.cur.execute("""
                CREATE TABLE `music` (
                  `music_id` INTEGER,
                  `music_name` TEXT,
                  `music_cover_image` TEXT,
                  `music_artist_name` TEXT,
                  `music_difficulty`  INTEGER,
                  `music_level` INTEGER,
                  `music_base_rate`  INTEGER
                );
              """)

    def fetch_music_info(self, music_id, music_difficulty):
        """
        楽曲idと楽曲の難易度から曲の情報をフェッチし返す
        :param music_id: 楽曲id
        :param music_difficulty: 楽曲の難易度(masterとか)
        :return music: 楽曲の情報
        """
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

    def fetch_music_id_list(self):
        """
        登録されている楽曲の楽曲idを難易度ごとにフェッチし返す
        :return expert_music_base_rate: expertの楽曲idのリスト
        :return music_base_rate: masterの楽曲idのリスト
        """
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

    def fetch_music_id(self, file_name):
        """
        登録されている楽曲の中からカバーイラストのファイル名から楽曲idをフェッチして返す
        :param file_name: カバーイラストのファイル名
        :return music_id: 楽曲id
        """
        sql = 'SELECT * FROM music WHERE "music_cover_image" = ?'
        self.cur.execute(sql, (file_name,))
        r = self.cur.fetchone()
        if r is None:
            return None
        else:
            return r[0]

    def update_music_info(self, music, music_shortage=None):
        """
        楽曲情報を更新する
        :param music: 楽曲情報
        :param music_shortage: 不足分の楽曲情報
        """
        sql = 'SELECT * FROM music WHERE music_id = ? AND music_difficulty = ?'
        self.cur.execute(sql, (music['music_id'], music['music_difficulty']))
        row = self.cur.fetchone()
        if row:
            sql = 'DELETE FROM music WHERE music_id = ? AND music_difficulty = ?'
            self.cur.execute(
                sql, (music['music_id'], music['music_difficulty']))
        if music_shortage:
            sql = """
            INSERT INTO music (
                music_id,
                music_name,
                music_cover_image,
                music_artist_name,
                music_difficulty,
                music_level,
                music_base_rate
            ) VALUES (?,?,?,?,?,?,?);"""
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
            sql = """
            INSERT INTO music (
                music_id,
                music_name,
                music_cover_image,
                music_artist_name,
                music_difficulty,
                music_level,
                music_base_rate
            ) VALUES (?,?,?,?,?,?,?)"""
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

    def search_music(self, data):
        """
        楽曲検索
        :param data: 検索するための楽曲名、レベル、難易度
        :return music: 楽曲情報
        """
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
                dic = {
                    'music_id': row[0],
                    'music_name': row[1],
                    'music_cover_image': row[2],
                    'music_artist_name': row[3],
                    'music_difficulty': row[4],
                    'music_level': row[5],
                    'music_base_rate': row[6]
                }
                music.append(dic)
            return music


class User:
    """
    各ユーザーのデータベースに計算結果を保存する
    """

    def __init__(self, user_hash):
        """
        事前処理: 新規ユーザーかを判定し、新規ユーザーであればデータベースを作成する
        :param user_hash: フレンドコードのハッシュ値
        """
        path = os.path.dirname(__file__)+'/user/'

        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        path += '{}.db'.format(user_hash)

        if os.path.exists(path):
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
        else:
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
            self.cur.execute("""
                CREATE TABLE `best` (
                  `music_id` INTEGER,
                  `music_name` TEXT,
                  `music_cover_image` TEXT,
                  `music_artist_name` TEXT,
                  `music_difficulty`  INTEGER,
                  `music_level` TEXT,
                  `music_base_rate`  INTEGER,
                  `music_score_highest`  INTEGER,
                  `music_rate_highest`  INTEGER
                );
              """)
            self.cur.execute("""
                CREATE TABLE `recent` (
                  `music_id` INTEGER,
                  `music_name` TEXT,
                  `music_cover_image` TEXT,
                  `music_artist_name` TEXT,
                  `music_difficulty`  INTEGER,
                  `music_level` TEXT,
                  `music_base_rate`  INTEGER,
                  `music_score`  INTEGER,
                  `music_rate`  INTEGER,
                  `music_play_date` TEXT
                );
              """)
            self.cur.execute("""
                CREATE TABLE `rate` (
                  `rate_display`  INTEGER,
                  `rate_highest` INTEGER,
                  `rate_best` INTEGER,
                  `rate_recent`  INTEGER,
                  `rate_max`  INTEGER,
                  `user_playCount` INTEGER,
                  `rate_execute_date` TEXT
                );
              """)
            self.cur.execute("""
                CREATE TABLE `user` (
                    `user_id` INTEGER,
                    `user_userName` TEXT,
                    `user_characterFileName` TEXT,
                    `user_characterLevel` INTEGER,
                    `user_friendCount` INTEGER,
                    `user_highestRating` INTEGER,
                    `user_level` INTEGER,
                    `user_playCount` INTEGER,
                    `user_playerRating` INTEGER,
                    `user_point` INTEGER,
                    `user_reincarnationNum` INTEGER,
                    `user_totalPoint` INTEGER,
                    `user_trophyName` TEXT,
                    `user_trophyType` INTEGER,
                    `user_webLimitDate` TEXT,
                    `user_friendCode` INTEGER,
                    `user_hash` TEXT,
                    `user_final_play_date` TEXT
                    PRIMARY KEY(`user_id`)
                );
              """)

    def update_best(self, best):
        """
        ベスト枠を削除してからベスト枠を更新する
        :param best: ベスト枠
        """
        self.cur.execute('DELETE FROM best')
        sql = """
        INSERT INTO best (
            music_id,
            music_name,
            music_cover_image,
            music_artist_name,
            music_difficulty,
            music_level,
            music_base_rate,
            music_score_highest,
            music_rate_highest
        ) VALUES (?,?,?,?,?,?,?,?)"""
        for music in best:
            self.cur.execute(
                sql, (
                    music['music_id'],
                    music['music_name'],
                    music['music_cover_image'],
                    music['music_artist_name'],
                    music['music_difficulty'],
                    music['music_level'],
                    music['music_base_rate'],
                    music['music_score_highest'],
                    music['music_rate_highest']
                )
            )
            self.con.commit()

    def update_recent(self, recent):
        """
        一度削除してからリセント候補枠を保存する
        :param recent: リセント枠
        """
        self.cur.execute('DELETE FROM recent')
        sql = """
        INSERT INTO recent (
            'music_id',
            'music_name',
            'music_cover_image',
            'music_artist_name',
            'music_difficulty',
            'music_level',
            'music_base_rate',
            'music_score',
            'music_rate',
            'music_play_date'
        ) VALUES (?,?,?,?,?,?,?,?)"""
        for music in recent:
            self.cur.execute(
                sql, (
                    music['music_id'],
                    music['music_name'],
                    music['music_cover_image'],
                    music['music_artist_name'],
                    music['music_difficulty'],
                    music['music_level'],
                    music['music_base_rate'],
                    music['music_score'],
                    music['music_rate'],
                    music['music_play_date']
                )
            )
            self.con.commit()

    def update_user_info(self, user):
        """
        ユーザー情報を保存する
        :param user: ユーザー情報
        """
        sql = 'SELECT * FROM user WHERE PlayCount = ?'
        self.cur.execute(sql, (user['PlayCount'],))
        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM user WHERE PlayCount = ?'
            self.cur.execute(sql, (user['PlayCount'],))
        sql = """
        INSERT INTO user (
            user_userName,
            user_characterFileName,
            user_characterLevel,
            user_friendCount,
            user_highestRating,
            user_level,
            user_playCount,
            user_playerRating,
            user_point,
            user_reincarnationNum,
            user_totalPoint,
            user_trophyName,
            user_trophyType,
            user_webLimitDate,
            user_friendCode,
            user_hash,
            user_final_play_date
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

        self.cur.execute(
            sql, (
                user['user_userName'],
                user['user_characterFileName'],
                user['user_characterLevel'],
                user['user_friendCount'],
                user['user_highestRating'],
                user['user_level'],
                user['user_playCount'],
                user['user_playerRating'],
                user['user_point'],
                user['user_reincarnationNum'],
                user['user_totalPoint'],
                user['user_trophyName'],
                user['user_trophyType'],
                user['user_webLimitDate'],
                user['user_friendCode'],
                user['user_hash'],
                user['user_final_play_date']
            )
        )
        self.con.commit()

    def update_rate(self, rate):
        """
        レートの推移を保存する
        :param rate: レート値
        """
        sql = 'SELECT * FROM rate WHERE user_playCount = ?'
        self.cur.execute(sql, (rate['user_playCount'],))

        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM rate WHERE user_playCount = ?'
            self.cur.execute(sql, (rate['user_playCount'],))

        sql = """
        INSERT INTO rate (
            rate_display,
            rate_highest,
            rate_best,
            rate_recent,
            rate_max,
            user_playCount,
            rate_execute_date
        ) VALUES (?,?,?,?,?,?,?)"""

        self.cur.execute(
            sql, (
                rate['rate_display'],
                rate['rate_highest'],
                rate['rate_best'],
                rate['rate_recent'],
                rate['rate_max'],
                rate['user_playCount'],
                rate['rate_execute_date']
            )
        )
        self.con.commit()

    def load_best(self):
        """
        ベスト枠をデータベースから読み込む
        :return best: ベスト枠
        """
        self.cur.execute("SELECT * FROM best")
        rows = self.cur.fetchall()
        if rows:
            best = []
            dif = {3: 'master', 2: 'expert'}
            for row in rows:
                dic = {
                    'music_id': row[0],
                    'music_name': row[1],
                    'music_cover_image': row[2],
                    'music_artist_name': row[3],
                    'music_difficulty': dif[row[4]],
                    'music_level': row[5],
                    'music_base_rate': row[6],
                    'music_score_highest': row[7],
                    'music_rate_highest': row[8],
                    'music_score_rank': func.score_to_rank(row[7])
                }
                best.append(dic)
            return best
        else:
            return None

    def load_recent(self):
        """
        リセント候補枠をデータベースから読み込む
        :return recent: リセント枠
        """
        self.cur.execute("SELECT * FROM recent")
        rows = self.cur.fetchall()
        if rows:
            recent = []
            dif = {3: 'master', 2: 'expert'}
            for row in rows:
                dic = {
                    'music_id': row[0],
                    'music_name': row[1],
                    'music_cover_image': row[2],
                    'music_artist_name': row[3],
                    'music_difficulty':  dif[row[4]],
                    'music_level': row[5],
                    'music_base_rate':  row[6],
                    'music_score':  row[7],
                    'music_rate':  row[8],
                    'music_play_date': row[9],
                    'music_score_rank': func.score_to_rank(row[7])
                }
                recent.append(dic)
            return recent
        else:
            return None

    def load_user(self):
        """
        ユーザー情報をデータベースから読み込む
        :return user: ユーザー情報
        """
        self.cur.execute('SELECT * FROM user')
        rows = self.cur.fetchall()
        if rows:
            user = []
            character_frame = ['normal', 'copper', 'silver', 'gold', 'gold', 'platina']
            trophy_type = ["normal", "copper", "silver", "gold", "platina"]
            for row in rows:
                dic = {
                    'user_id': row[0],
                    'user_userName': row[1],
                    'user_characterFileName': character_frame[int(row[2]/5)],
                    'user_characterLevel': row[3],
                    'user_friendCount': row[4],
                    'user_highestRating': row[5],
                    'user_level': row[6],
                    'user_playCount': row[7],
                    'user_playerRating': row[8],
                    'user_point': row[9],
                    'user_reincarnationNum': row[10],
                    'user_totalPoint': row[11],
                    'user_trophyName': row[12],
                    'user_trophyType': trophy_type[row[13]],
                    'user_webLimitDate': row[14],
                    'user_friendCode': row[15],
                    'user_hash': row[16],
                    'user_final_play_date': row[17]
                }
                user.append(dic)
            return user
        else:
            return None

    def load_rate(self):
        """
        レートの推移をデータベースから読み込む
        :return rate: レートの推移
        """
        self.cur.execute('SELECT * FROM rate')
        rows = self.cur.fetchall()
        if rows:
            rate = []
            for row in rows:
                dic = {
                    'rate_display': row[0],
                    'rate_highest': row[1],
                    'rate_best': row[2],
                    'rate_recent': row[3],
                    'rate_max': row[4],
                    'user_playCount': row[5],
                    'rate_execute_date': row[6]
                }
                rate.append(dic)
            return rate
        else:
            return None


class Admin:
    """
    管理用のデータベース
    """

    def __init__(self):
        """
        事前処理
        """
        path = os.path.dirname(__file__)+'/database/admin.db'
        if os.path.exists(path):
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
        else:
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()
            self.cur.execute("""
        CREATE TABLE `user` (
            `user_userName`  TEXT,
            `user_friendCode`  TEXT,
            `user_hash`  TEXT,
            `user_playCount` INTEGER,
            `rate_display`  INTEGER,
            `rate_highest` INTEGER,
            `rate_best` INTEGER,
            `rate_recent`  INTEGER,
            `rate_max`  INTEGER
        );""")

    def update_user_admin(self, data):
        """
        ユーザ管理データベースを更新する
        :param data: ユーザーを管理するための情報
        """
        sql = 'SELECT * FROM user WHERE user_hash = ?'
        self.cur.execute(sql, (data['user_hash'],))
        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM user WHERE Hash = ?'
            self.cur.execute(sql, (data['user_hash'],))
        sql = """
        INSERT INTO user (
            user_userName,
            user_friendCode,
            user_hash,
            user_playCount,
            rate_display,
            rate_highest,
            rate_best,
            rate_recent,
            rate_max
        ) VALUES (?,?,?,?,?,?,?,?,?)"""

        self.cur.execute(
            sql, (
                data['user_userName'],
                data['user_friendCode'],
                data['user_hash'],
                data['user_playCount'],
                data['rate_display'],
                data['rate_highest'],
                data['rate_best'],
                data['rate_recent'],
                data['rate_max']
            )
        )
        self.con.commit()

    def load_admin_data_base(self):
        """
        ユーザ管理データベースから読み込む
        :return user:　ユーザー情報
        """
        self.cur.execute('SELECT * FROM user')
        rows = self.cur.fetchall()
        if rows:
            user = []
            for row in rows:
                dic = {
                    'user_userName': row[0],
                    'user_friendCode': row[1],
                    'user_hash': row[2],
                    'user_playCount': row[3],
                    'rate_display': row[4],
                    'rate_highest': row[5],
                    'rate_best': row[6],
                    'rate_recent': row[7],
                    'rate_max': row[8]
                }
                user.append(dic)
            return user
        else:
            return None

    def search_user(self, user):
        """
        ユーザーを検索する
        :param user: 検索するためのやつ
        :return user:
        """
        sql = """
        SELECT * FROM user 
            Where 
                user_userName = ? or 
                user_friendCode = ? or 
                user_hash = ? or 
                user_playCount = ? or 
                rate_display = ? or 
                rate_highest = ? or 
                rate_best = ? or 
                rate_recent = ? or
                rate_max = ?"""

        self.cur.execute(
            sql, (
                user['user_userName'],
                user['user_friendCode'],
                user['user_hash'],
                user['user_playCount'],
                user['rate_display'],
                user['rate_highest'],
                user['rate_best'],
                user['rate_recent'],
                user['rate_max']
            )
        )

        rows = self.cur.fetchall()
        if rows:
            user = []
            for row in rows:
                dic = {
                    'user_userName': row[0],
                    'user_friendCode': row[1],
                    'user_hash': row[2],
                    'user_playCount': row[3],
                    'rate_display': row[4],
                    'rate_highest': row[5],
                    'rate_best': row[6],
                    'rate_recent': row[7],
                    'rate_max': row[8]
                }
                user.append(dic)
            return user
        else:
            return self.load_admin_data_base()
