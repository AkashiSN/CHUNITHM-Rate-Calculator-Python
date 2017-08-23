#!/usr/bin/env python3

import sqlite3
import os
from chunithm import func


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
                  `music_rate_highest`  INTEGER,
                  `music_socre_max` INTEGER
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
                  `user_play_count` INTEGER,
                  `execute_date` TEXT
                );
              """)
            self.cur.execute("""
                CREATE TABLE `user` (
                    `user_id` INTEGER,
                    `user_name` TEXT,
                    `user_character_file_name` TEXT,
                    `user_character_level` INTEGER,
                    `user_friend_count` INTEGER,
                    `user_highest_rating` INTEGER,
                    `user_level` INTEGER,
                    `user_play_count` INTEGER,
                    `user_player_rating` INTEGER,
                    `user_point` INTEGER,
                    `user_reincarnation_num` INTEGER,
                    `user_total_point` INTEGER,
                    `user_trophy_name` TEXT,
                    `user_trophy_type` INTEGER,
                    `user_web_limit_date` TEXT,
                    `user_friend_code` INTEGER,
                    `user_hash` TEXT,
                    `user_final_play_date` TEXT,
                    `execute_date` TEXT,
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
            music_rate_highest,
            music_socre_max
        ) VALUES (?,?,?,?,?,?,?,?,?,?)"""
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
                    music['music_rate_highest'],
                    music['music_score_max']
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
        ) VALUES (?,?,?,?,?,?,?,?,?,?)"""
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
        sql = 'SELECT * FROM user WHERE user_play_count = ?'
        self.cur.execute(sql, (user['user_play_count'],))
        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM user WHERE user_play_count = ?'
            self.cur.execute(sql, (user['user_play_count'],))
        sql = """
        INSERT INTO user (
            user_name,
            user_character_file_name,
            user_character_level,
            user_friend_count,
            user_highest_rating,
            user_level,
            user_play_count,
            user_player_rating,
            user_point,
            user_reincarnation_num,
            user_total_point,
            user_trophy_name,
            user_trophy_type,
            user_web_limit_date,
            user_friend_code,
            user_hash,
            user_final_play_date,
            execute_date
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

        self.cur.execute(
            sql, (
                user['user_name'],
                user['user_character_file_name'],
                user['user_character_level'],
                user['user_friend_count'],
                user['user_highest_rating'],
                user['user_level'],
                user['user_play_count'],
                user['user_player_rating'],
                user['user_point'],
                user['user_reincarnation_num'],
                user['user_total_point'],
                user['user_trophy_name'],
                user['user_trophy_type'],
                user['user_web_limit_date'],
                user['user_friend_code'],
                user['user_hash'],
                user['user_final_play_date'],
                user['execute_date']
            )
        )
        self.con.commit()

    def update_rate(self, rate):
        """
        レートの推移を保存する
        :param rate: レート値
        """
        sql = 'SELECT * FROM rate WHERE user_play_count = ?'
        self.cur.execute(sql, (rate['user_play_count'],))

        r = self.cur.fetchall()
        if r:
            sql = 'DELETE FROM rate WHERE user_play_count = ?'
            self.cur.execute(sql, (rate['user_play_count'],))

        sql = """
        INSERT INTO rate (
            rate_display,
            rate_highest,
            rate_best,
            rate_recent,
            rate_max,
            user_play_count,
            execute_date
        ) VALUES (?,?,?,?,?,?,?)"""

        self.cur.execute(
            sql, (
                rate['rate_display'],
                rate['rate_highest'],
                rate['rate_best'],
                rate['rate_recent'],
                rate['rate_max'],
                rate['user_play_count'],
                rate['execute_date']
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
            for row in rows:
                dic = {
                    'music_id': row[0],
                    'music_name': row[1],
                    'music_cover_image': row[2],
                    'music_artist_name': row[3],
                    'music_difficulty':  row[4],
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
                    'user_name': row[1],
                    'user_character_file_name': row[2],
                    'user_character_level': character_frame[int(row[3]/5)],
                    'user_friend_count': row[4],
                    'user_highest_rating': row[5],
                    'user_level': row[6],
                    'user_play_count': row[7],
                    'user_player_rating': row[8],
                    'user_point': row[9],
                    'user_reincarnation_num': row[10],
                    'user_total_point': row[11],
                    'user_trophy_name': row[12],
                    'user_trophy_type': trophy_type[row[13]],
                    'user_web_limit_date': row[14],
                    'user_friend_code': row[15],
                    'user_hash': row[16],
                    'user_final_play_date': row[17],
                    'execute_date': row[18]
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
                    'user_play_count': row[5],
                    'rate_execute_date': row[6]
                }
                rate.append(dic)
            return rate
        else:
            return None

