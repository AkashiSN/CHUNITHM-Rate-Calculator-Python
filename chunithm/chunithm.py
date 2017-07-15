#!/usr/bin/env python3

import hashlib
import math
from datetime import datetime
from chunithm import func
from chunithm import db


class Calculate:
    def __init__(self, user_id):
        self.user_id = user_id
        self.music_base_rate = db.Music()
        self.user_friend_code = func.fetch_user_friend_code(self.user_id)
        self.user_hash = hashlib.sha256(str(self.user_friend_code).encode('utf8')).hexdigest()
        self.user_data_base = db.User(self.user_hash)
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
                        music_info = self.music_base_rate.fetch_music_info(music_id, music_difficulty)
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
                music_id = self.music_base_rate.fetch_music_id(play["musicFileName"])
                music_info = self.music_base_rate.fetch_music_info(music_id, difficulty_map[play["levelName"]])
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
                        music_recent_date_list = sorted(music_recent_list, key=lambda x: datetime.strptime(x["music_play_date"], '%Y-%m-%d %H:%M:%S'), reverse=True)
                        music_recent_date_list.pop()
                        music_recent_list = sorted(music_recent_date_list, key=lambda x: x["music_rate"], reverse=True)

        rate = {}
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
        admin_data = db.Admin()
        data = {
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
        admin_data.update_user_admin(data)

    def run(self):
        self.calculate_best_rate()
        self.calculate_recent_rate()
        self.update_user()
        self.calculate_rate()
        self.update_admin()
        return self.user_hash

#Best枠の時の表示
def DispBest(Hash):
    DataBase = db.UserDataBase(Hash)
    Best = DataBase.LoadBest()
    User = DataBase.LoadUser()
    Rate = DataBase.LoadRate()
    return Best,User,Rate

#Recent枠の時の表示
def DispRecent(Hash):
    DataBase = db.UserDataBase(Hash)
    Recent = DataBase.LoadRecent()
    User = DataBase.LoadUser()
    Rate = DataBase.LoadRate()
    return Recent,User,Rate

#Graphの表示
def DispGraph(Hash):
    DataBase = db.UserDataBase(Hash)
    Rate = DataBase.LoadRate()
    User = DataBase.LoadUser()
    return User,Rate

#Toolの表示
def DispTools(Hash):
    DataBase = db.UserDataBase(Hash)
    Rate = DataBase.LoadRate()
    User = DataBase.LoadUser()
    return User,Rate

#譜面定数の確認
def CheckMusic(userId):
    MusicIdList = func.Get_MusicIdList(userId)
    DataBase = db.LoadBaseRate()
    BaseRateList = DataBase.Get_BaseRateList()
    NoneMusicList = []
    ExistMusicList = []

    for level in range(2,4):
        for MusicId in MusicIdList[level-2]:
            if MusicId in BaseRateList[level-2]:
                Music = DataBase.Get_BaseRate(MusicId,level)
                if Music['BaseRate'] is not None:
                    BaseRate = Music['BaseRate']
                    Dic = {
                        'MusicId':MusicId,
                        'MusicName':Music['MusicName'],
                        'MusicImage':Music['Image'],
                        'ArtistName':Music['ArtistName'],
                        'Level':level,
                        'BaseRate':BaseRate,
                        'AirPlus':Music['AirPlus']
                    }
                    ExistMusicList.append(Dic)
                    continue
            Music = func.Get_BestScore(userId,MusicId)
            Dic = {
                'MusicId':MusicId,
                'MusicName':Music['musicName'],
                'MusicImage':Music['musicFileName'],
                'ArtistName':Music['artistName'],
                'Level':level,
                'BaseRate':None,
                'AirPlus':False
            }
            NoneMusicList.append(Dic)
            DataBase.SetMusic(Dic,True)
    return NoneMusicList,ExistMusicList

#譜面定数の更新
def SetMusic(UserId,MusicId,Level,BaseRate):
    Music = func.Get_BestScore(UserId, MusicId)
    DataBase = db.LoadBaseRate()
    Dic = {
        'MusicId':MusicId,
        'Level':Level,
        'MusicName':Music['musicName'],
        'Image':Music['musicFileName'],
        'ArtistName':Music['artistName'],
        'BaseRate':BaseRate
    }
    DataBase.SetMusic(Dic)

#楽曲の検索
def SearchMusic(UserId,Dic):
    DataBase = db.LoadBaseRate()
    MusicList = DataBase.SerchMusic_db(Dic)
    MusicIdList = {x['MusicId']:idx for idx,x in enumerate(MusicList) if x['Level'] == 2},{x['MusicId']:idx for idx,x in enumerate(MusicList) if x['Level'] == 3}
    GenreList = func.Get_Genre(UserId,Dic['Genre'],Dic['DiffLevel'])
    ResultList = []
    if Dic['DiffLevel']:
        for MusicId in GenreList:
            if MusicId in MusicIdList[int(Dic['DiffLevel'])-2]:
                idx = MusicIdList[int(Dic['DiffLevel'])-2][MusicId]
                ResultList.append(MusicList[idx])
    else:
        for level in range(2,4):
            for MusicId in GenreList[level-2]:
                if MusicId in MusicIdList[level-2]:
                    idx = MusicIdList[level-2][MusicId]
                    ResultList.append(MusicList[idx])
    return ResultList

