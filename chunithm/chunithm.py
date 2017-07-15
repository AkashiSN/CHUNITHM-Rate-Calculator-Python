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
        self.rate = []

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

        rate = []
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

        now_date = datetime.now().strptime("%Y-%m-%d %H:%M:%S")
        user = {
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

        self.user_data_base.update_user_info(user)

# レートを計算してデータベースに保存する
def CalcRate(userId):
    '''レートを計算してデータベースに保存する'''

    Base = db.LoadBaseRate()
    FriendCode = func.Get_FriendCode(userId)
    if FriendCode is None:
        return None

    Hash = hashlib.sha256(str(FriendCode).encode('utf8')).hexdigest()

    Rating = {}
    DataBase = db.UserDataBase(Hash)

    # Best枠について
    MusicIdList = func.Get_MusicIdList(userId)  # MusicIdのリストの取得
    if MusicIdList is None:
        return None
    Musics = []
    i = 0
    for Level in range(2,4):
        MusicBestScore = func.Get_DiffList(userId,"1990"+str(Level))  # エキスパート(19902)とマスター(19903)の曲別最大スコアのリストの取得
        if MusicBestScore is None:
            return None
        for MusicId in MusicIdList[Level-2]:
            for Music in MusicBestScore['userMusicList']:
                if Music['musicId'] == MusicId:
                    MusicDetail = Base.Get_BaseRate(MusicId,Level)
                    if MusicDetail is None or MusicDetail['BaseRate'] is None:
                        continue
                    else:
                        Dic = {
                            'MusicId':MusicId,
                            'Level':Level,
                            'MusicName':MusicDetail['MusicName'],
                            'Image':MusicDetail['Image'],
                            'BaseRate':MusicDetail['BaseRate'],
                            'Rate':func.Score2Rate(Music['scoreMax'],MusicDetail['BaseRate']),
                            'Score':Music['scoreMax']
                        }
                        Musics.append(Dic)
    #ソート
    Best = sorted(Musics,key=lambda x:x["Rate"],reverse=True)
    Rate = {'BestRate':0,'MaxBestRate':0}
    for Music in Best:
        if i < 30:
            Music['MaxScore'] = None
            Rate['BestRate'] += Music['Rate']
            if i == 0:
                Rate['MaxBestRate'] =  Music['Rate']
            elif i == 29:
                Rate['MinBestRate'] =  Music['Rate']
        else:
            if Music['Score'] >= 1007500:
                Music['MaxScore'] = None
            else:
                MaxScore = func.Rate2Score(Music['BaseRate'],Rate['MinBestRate'])
                if MaxScore <= 1007500 and MaxScore > 0 and MaxScore - Music['Score'] > 0:
                    Music['MaxScore'] = MaxScore
                else:
                    Music['MaxScore'] = None
        i+=1

    #データーベースに保存
    DataBase.SetBest(Best)

    #Recent
    Playlog = func.Get_PlayLog(userId)
    if Playlog is None:
        return None
    Recent = DataBase.LoadRecent()
    LevelMap = {'master':3,"expert":2}
    FinalPlayDate = Playlog['userPlaylogList'][0]['userPlayDate'][0:-2]

    Musics = []
    for Play in Playlog['userPlaylogList'][0:30]:
        if Play['levelName'] == 'expert' or Play['levelName'] == 'master':
            MusicId = Base.Get_MusicId(Play['musicFileName'])
            if MusicId is None:
                continue
            MusicDetail = Base.Get_BaseRate(MusicId,LevelMap[Play['levelName']])
            if MusicDetail is None or MusicDetail['BaseRate'] is None:
                continue
            else:
                Dic = {
                    'MusicId':MusicId,
                    'Level':LevelMap[Play['levelName']],
                    'MusicName':MusicDetail['MusicName'],
                    'Image':MusicDetail['Image'],
                    'BaseRate':MusicDetail['BaseRate'],
                    'Rate':func.Score2Rate(Play['score'],MusicDetail['BaseRate']),
                    'Score':Play['score'],
                    'PlayDate':Play['userPlayDate'][0:-2]
                }
                Musics.append(Dic)
    if Recent is None:
        #レート順にソート
        Recent = sorted(Musics,key=lambda x:x['Rate'],reverse=True)
    else:
        #レート順にソート
        Recent = sorted(Recent,key=lambda x:x['Rate'],reverse=True)
        if len(Recent) > 10:
            UserData = DataBase.LoadUser()
            #UserDataがゼロではなかったら
            if len(UserData):
                OldDate = datetime.strptime(UserData[-1]['FinalPlayDate'], '%Y-%m-%d %H:%M:%S')
                for Play in Musics:
                    NowDate = datetime.strptime(Play['PlayDate'], '%Y-%m-%d %H:%M:%S')
                    #最後に実行されたときの曲と現在の曲の新旧
                    if NowDate > OldDate:
                        #Recent枠の最小と比較
                        if Play['Rate'] > Recent[9]['Rate']:
                            #Recent枠の最小と入れ替え
                            Recent[-1]['MusicId'] = Play['MusicId']
                            Recent[-1]['Level'] = Play['Level']
                            Recent[-1]['MusicName'] = Play['MusicName']
                            Recent[-1]['Image'] = Play['Image']
                            Recent[-1]['BaseRate'] = Play['BaseRate']
                            Recent[-1]['Score'] = Play['Score']
                            Recent[-1]['Rate'] = Play['Rate']
                            Recent[-1]['PlayDate'] = Play['PlayDate']
                        elif Play['Score'] >= 1007500:
                            pass
                        elif Play['Score'] >= Recent[-1]['Score']:
                            pass
                        else:
                            #プレイ日時順にソート
                            Recent = sorted(Recent,key=lambda x:datetime.strptime(x['PlayDate'], '%Y-%m-%d %H:%M:%S'),reverse=True)
                            #Recent候補枠の一番古い曲と入れ替え
                            Recent[-1]['MusicId'] = Play['MusicId']
                            Recent[-1]['Level'] = Play['Level']
                            Recent[-1]['MusicName'] = Play['MusicName']
                            Recent[-1]['Image'] = Play['Image']
                            Recent[-1]['BaseRate'] = Play['BaseRate']
                            Recent[-1]['Score'] = Play['Score']
                            Recent[-1]['Rate'] = Play['Rate']
                            Recent[-1]['PlayDate'] = Play['PlayDate']
                            #レート順にソート
                            Recent = sorted(Recent,key=lambda x:x['Rate'],reverse=True)
                    else:
                        pass
            else:
                pass
        else:
            pass

    RecentRates = 0
    i = 0
    for Music in Recent:
        if i < 10:
            RecentRates += Music['Rate']
            i += 1

    #ユーザーデータ
    UserInfo = func.Get_UserData(userId)
    if UserInfo is None:
        return None
    else:
        UserInfo = UserInfo['userInfo']

    NowDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    User = {
        'TotalPoint':UserInfo['totalPoint'],
        'TrophyType':UserInfo['trophyType'],
        'WebLimitDate':UserInfo['webLimitDate'][0:-2],
        'CharacterFileName':UserInfo['characterFileName'],
        'FriendCount':UserInfo['friendCount'],
        'Point':UserInfo['point'],
        'PlayCount':UserInfo['playCount'],
        'CharacterLevel':UserInfo['characterLevel'],
        'TrophyName':UserInfo['trophyName'],
        'ReincarnationNum':UserInfo['reincarnationNum'],
        'UserName':UserInfo['userName'],
        'Level':UserInfo['level'],
        'FriendCode':FriendCode,
        'Hash':Hash,
        'FinalPlayDate':FinalPlayDate,
        'ExecuteDate': NowDate
    }


    #データベースに保存
    DataBase.SetRecent(Recent)

    #レート計算
    DispRate = (UserInfo['playerRating'] / 100.0)
    BestRate = math.floor((Rate['BestRate'] / 30) * 100) /100
    Rating = {
        'DispRate':DispRate,
        'HighestRating':(UserInfo['highestRating'] / 100.0),
        'MaxRate':(math.floor(((Rate['BestRate'] + Rate['MaxBestRate'] * 10) / 40) * 100) / 100),
        'BestRate':BestRate,
        #'RecentRate':(math.floor(((DispRate * 40 - BestRate * 30) / 10) * 100) / 100),
        'RecentRate':(math.floor((RecentRates /10)*100)/100) ,
        'Credits':UserInfo['playCount'],
        'ExecuteDate': NowDate
    }
    #データベースに保存
    DataBase.SetRate(Rating)

    #データベースに保存
    DataBase.SetUser(User)

    Admin = db.AdminDataBase()
    Data = {
        'UserName':UserInfo['userName'],
        'FriendCode':FriendCode,
        'Hash':Hash,
        'Credits':UserInfo['playCount'],
        'DispRate':DispRate,
        'HighestRating':Rating['HighestRating'],
        'MaxRate':Rating['MaxRate'],
        'BestRate':BestRate,
        'RecentRate':Rating['RecentRate'],
    }
    Admin.SetData(Data)

    return Hash

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

