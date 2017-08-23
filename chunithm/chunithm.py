#!/usr/bin/env python3
import hashlib
import math
from datetime import datetime
from chunithm import models
from chunithm import func
from chunithm import database
from chunithm import db


class Calculate:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_friend_code = func.fetch_user_friend_code(self.user_id)
        self.user_hash = hashlib.sha256(str(self.user_friend_code).encode('utf8')).hexdigest()
        self.user_data_base = database.User(self.user_hash)
        self.rate = {}
        self.user = {}

    def calculate_best_rate(self):
        """
        ベスト枠を計算してデーターベースに保存する
        """
        music_id_list = func.fetch_music_id_list(self.user_id)
        music_best_list = []

        for music_difficulty in range(2, 4):
            music_score_highest_list = func.fetch_difficulty_list(self.user_id, "1990"+str(music_difficulty))
            for music_id in music_id_list[music_difficulty-2]:
                for music in music_score_highest_list["userMusicList"]:
                    if music["musicId"] == music_id:
                        music_info_class = models.Music.query.filter_by(music_id=music_id,music_difficulty=music_difficulty).first()
                        music_info = music_info_class.fetch_music_info()
                        if music_info is None or music_info['music_base_rate'] is None:
                            continue
                        else:
                            music_info["music_score_highest"] = music["scoreMax"]
                            music_info["music_rate_highest"] = func.score_to_rate(music["scoreMax"], music_info["music_base_rate"])
                            music_best_list.append(music_info)
        music_best_list = sorted(music_best_list, key=lambda x: x["music_rate_highest"], reverse=True)
        rate = {"best_rate_sum": 0, "max_best_rate": 0, "min_best_rate": 0}
        for i, music in enumerate(music_best_list):
            if i < 30:
                music["music_score_max"] = None
                rate["best_rate_sum"] += music["music_rate_highest"]
                if i == 0:
                    rate["max_best_rate"] = music["music_rate_highest"]
                elif i == 29:
                    rate["min_best_rate"] = music["music_rate_highest"]
            else:
                if music["music_score_highest"] >= 1007500:
                    music["music_score_max"] = None
                else:
                    music_score_max = func.rate_to_score(music["music_base_rate"], rate["min_best_rate"])
                    if 0 < music_score_max < 1007500 and music_score_max - music["music_score_highest"] > 0:
                        music["music_score_max"] = music_score_max
                    else:
                        music["music_score_max"] = None

        self.rate["best"] = rate
        self.user_data_base.update_best(music_best_list)

    def calculate_recent_rate(self):
        """
        リセント候補枠を計算してデーターベースに保存する
        """
        play_log = func.fetch_play_log(self.user_id)
        music_recent_list = self.user_data_base.load_recent()
        difficulty_map = {"master": 3, "expert": 2}
        play_log_list = []

        for play in play_log["userPlaylogList"][0:30]:
            if play["levelName"] == "expert" or play["levelName"] == "master":
                music_info_class = models.Music.query.filter_by(music_cover_image=play["musicFileName"],
                                                              music_difficulty=difficulty_map[play["levelName"]]).first()
                music_info = music_info_class.fetch_music_info()
                if music_info is None or music_info["music_base_rate"] is None:
                    continue
                else:
                    music_info["music_score"] = play["score"]
                    music_info["music_rate"] = func.score_to_rate(play["score"], music_info["music_base_rate"])
                    music_info["music_play_date"] = play["userPlayDate"][0:-2]
                    play_log_list.append(music_info)

        # 初回実行の場合
        if music_recent_list is None:
            music_recent_list = sorted(play_log_list, key=lambda x: x["music_rate"], reverse=True)
        else:
            # リセント枠は最小でも10曲以上でないと計算できない
            if 10 <= len(music_recent_list) <= 30:
                user_data = self.user_data_base.load_user()
                old_date = datetime.strptime(user_data[-1]["user_final_play_date"], '%Y-%m-%d %H:%M:%S')
                for play in play_log_list:
                    now_date = datetime.strptime(play["music_play_date"], '%Y-%m-%d %H:%M:%S')
                    # 現在の楽曲がリセント枠に保存されている最終プレイ日時よりも新しい場合
                    if now_date > old_date:
                        # リセント候補枠の最小レート値よりも現在の楽曲のレート値のほうが大きい場合
                        if play["music_rate"] > music_recent_list[-1]["music_rate"]:
                            # リセント候補枠の最小レートを削除する
                            music_recent_list.pop()
                            music_recent_list.append(play)
                            music_recent_list = sorted(music_recent_list, key=lambda x: x["music_rate"], reverse=True)
                            continue
                        # 現在の楽曲がSSSの場合
                        if play["music_score"] != 1007500:
                            continue
                        # スコア順にソート
                        music_recent_score_list = sorted(music_recent_list, key=lambda x: x["music_score"], reverse=True)
                        # 現在の楽曲のスコアがリセント候補枠の最小スコア以上の場合
                        if play["music_score"] >= music_recent_score_list[-1]["music_score"]:
                            continue
                        # どれも当てはまらなかったらリセント候補枠の一番古いレート値を削除
                        music_recent_date_list = sorted(music_recent_list,
                                                        key=lambda x: datetime.strptime(x["music_play_date"], '%Y-%m-%d %H:%M:%S'),
                                                        reverse=True)
                        music_recent_date_list.pop()
                        music_recent_list = sorted(music_recent_date_list, key=lambda x: x["music_rate"], reverse=True)

        rate = {"recent_rate_sum":0}
        for i, music in enumerate(music_recent_list):
            if i < 10:
                rate["recent_rate_sum"] += music["music_rate"]

        self.rate["recent"] = rate
        self.user_data_base.update_recent(music_recent_list)

    def update_user(self):
        """
        ユーザーデータをデータベースに保存する
        """
        user_data = func.fetch_user_data(self.user_id)
        user_data = user_data["userInfo"]
        play_log = func.fetch_play_log(self.user_id)
        final_play_date = play_log['userPlaylogList'][0]['userPlayDate'][0:-2]

        now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = {
            'user_name': user_data["userName"],
            'user_character_file_name': user_data["characterFileName"],
            'user_character_level': user_data["characterLevel"],
            'user_friend_count': user_data["friendCount"],
            'user_highest_rating': user_data["highestRating"],
            'user_level': user_data["level"],
            'user_play_count': user_data["playCount"],
            'user_player_rating': user_data["playerRating"],
            'user_point': user_data["point"],
            'user_reincarnation_num': user_data["reincarnationNum"],
            'user_total_point': user_data["totalPoint"],
            'user_trophy_name': user_data["trophyName"],
            'user_trophy_type': user_data["trophyType"],
            'user_web_limit_date': user_data["webLimitDate"][0:-2],
            'user_friend_code': self.user_friend_code,
            'user_hash': self.user_hash,
            'user_final_play_date': final_play_date,
            'execute_date': now_date
        }
        self.rate["display"] = user_data["playerRating"] / 100.0
        self.rate["highest"] = user_data["highestRating"] / 100.0
        self.user["user_play_count"] = user_data["playCount"]
        self.user["user_name"] = user_data["userName"]
        self.user["execute_date"] = now_date
        self.user_data_base.update_user_info(user_info)

    def calculate_rate(self):
        """
        レートを計算してデータベースに保存する
        """
        rate = {
            'rate_display': self.rate["display"],
            'rate_highest': self.rate["highest"],
            'rate_best': math.floor((self.rate["best"]["best_rate_sum"] /30) * 100) / 100,
            'rate_recent': math.floor((self.rate["recent"]["recent_rate_sum"] / 10) * 100) / 100,
            'rate_max': math.floor(((self.rate["best"]["best_rate_sum"] + self.rate["best"]["max_best_rate"] * 10 ) / 40) * 100) /100,
            'user_play_count': self.user["user_play_count"],
            'execute_date': self.user["execute_date"]
        }

        self.rate["admin"] = rate
        self.user_data_base.update_rate(rate)

    def update_admin(self):
        """
        管理用データベースにユーザー情報を保存する
        """
        manage = Manage()
        user_data = {
            'user_name': self.user["user_name"],
            'user_friend_code': self.user_friend_code,
            'user_hash': self.user_hash,
            'user_play_count': self.user["user_play_count"],
            'rate_display': self.rate["admin"]["rate_display"],
            'rate_highest': self.rate["admin"]["rate_highest"],
            'rate_best': self.rate["admin"]["rate_best"],
            'rate_recent': self.rate["admin"]["rate_recent"],
            'rate_max': self.rate["admin"]["rate_max"]
        }
        manage.update_user_data(user_data)

    def run(self):
        """
        まとめて実行する
        :return: user_hash
        """
        self.calculate_best_rate()
        self.calculate_recent_rate()
        self.update_user()
        self.calculate_rate()
        self.update_admin()
        return self.user_hash


class Manage:
    """色々管理するやつ"""
    def __init__(self):
        pass

    def check_music_list(self, user_id):
        """
        データベースに未登録の楽曲のみを追加する
        :param user_id: ユーザーid
        """
        for music_level in range(11,15):
            music_id_list = func.fetch_music_level_list(user_id, music_level)
            for plus in ("levelList", "levelPlusList"):
                for music_id in music_id_list[plus]:
                    music_difficulty = music_id_list['difLevelMap'][str(music_id)]
                    music = models.Music.query.filter_by(music_id=music_id, music_difficulty=music_difficulty).one_or_none()
                    if music is None:
                        fetch_data = func.fetch_music_score_highest(user_id, music_id)
                        plus_list = {"levelList": '', "levelPlusList": '+'}
                        music = {
                            'music_id': music_id,
                            'music_name': fetch_data['musicName'],
                            'music_cover_image': fetch_data['musicFileName'],
                            'music_artist_name': fetch_data['artistName'],
                            'music_difficulty': music_id_list['difLevelMap'][str(music_id)],
                            'music_level': str(music_level) + plus_list[plus],
                            'music_base_rate': 0
                        }
                        new_music = models.Music(music)
                        db.session.add(new_music)
                        db.session.commit()

    def update_music_info(self, music_id, music_difficulty, music_base_rate):
        """
        楽曲情報を更新する
        :param music_id: 楽曲id
        :param music_difficulty: 楽曲の難易度
        :param music_base_rate: 楽曲の譜面定数
        """
        music = models.Music.query.filter_by(music_id=music_id, music_difficulty=music_difficulty).first()
        music.music_base_rate = music_base_rate
        db.session.commit()

    def search_music(self, music_difficulty,music_level,music_name):
        """
        楽曲情報を検索する
        :param music_difficulty: 楽曲の難易度
        :param music_level: 楽曲のレベル
        :param music_name: 楽曲の名前
        :return: 結果
        """
        music_list = models.Music.query.filter_by(music_difficulty=music_difficulty,
                                                     music_level=music_level,music_name="%"+music_name+"%").all()
        return music_list

    def update_user_data(self, user_data):
        """
        ユーザの情報を更新する
        :param user_data: ユーザーデータ
        """
        user = models.User.query.filter_by(user_hash=user_data['user_hash']).first()
        if user is None:
            new_user = models.User(user_data)
            db.session.add(new_user)
            db.session.commit()
        else:
            user.user_play_count = user_data['user_play_count']
            user.rate_display = user_data['rate_display']
            user.rate_highest = user_data['rate_highest']
            user.rate_best = user_data['rate_best']
            user.rate_recent = user_data['rate_recent']
            user.rate_max = user_data['rate_max']
            db.session.commit()
