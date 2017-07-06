#!/usr/bin/env python3

import json
import requests
import math
from flask import render_template


def init_errors(app):
    @app.errorhandler(404)
    def page_not_found():
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden():
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def general_error():
        return render_template('errors/500.html'), 500

    @app.errorhandler(405)
    def gateway_error():
        return render_template('errors/405.html'), 405


def extraction_user_id(post_data):
    """
    ポストデータからuser_idを抽出
    :param post_data: ポストデータ
    :return user_id: ユーザーid
    """
    tmp = post_data.split(';')
    for tmp1 in tmp:
        if 'userId' in tmp1:
            return tmp1.split('=')[1]
    return None


def fetch_user_id(sega_id, password):
    """
    ログインしてUserIdを取得
    :param sega_id: セガid
    :param password: パスワード
    :return user_id: ユーザーid
    """
    url = 'https://chunithm-net.com/Login/SegaIdLoginApi'
    parm = {'segaId': sega_id, 'password': password}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return None
    else:
        return str(re.json()['sessionIdList'][0])


def fetch_music_id_list(user_id):
    """
    music_level11以上のmusic_idのリストを取得
    :param user_id: ユーザーid
    :return music_id_list: 難易度master楽曲idのリスト
    :return expert_music_id_list: 難易度expert楽曲idのリスト
    """
    url = 'https://chunithm-net.com/ChuniNet/GetUserMusicLevelApi'
    music_id_list = []
    expert_music_id_list = []
    for music_level in range(11, 14):
        parm = {'userId': user_id, 'level': music_level}
        re = requests.post(url, data=json.dumps(parm))
        if re is None:
            return None
        json_data = re.json()
        if json_data is None:
            return None
        music_id_list += json_data['levelList']
        music_id_list += json_data['levelPlusList']
        for Id, dif in json_data['difLevelMap'].items():
            if dif == 2:
                expert_music_id_list.append(int(Id))

    music_id_list = list(set(music_id_list))
    expert_music_id_list = list(set(expert_music_id_list))
    return expert_music_id_list, music_id_list


def fetch_music_score_highest(user_id, music_id):
    """
    楽曲の詳細情報を取得
    :param user_id: ユーザーid
    :param music_id: 楽曲id
    :return json_data: 取得したデータ
    """
    url = 'https://chunithm-net.com/ChuniNet/GetUserMusicDetailApi'
    parm = {'userId': user_id, 'musicId': music_id}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return None
    json_data = json.loads(re.text, 'utf-8')
    return json_data


#
def fetch_difficulty_list(user_id, music_difficulty):
    """
    各難易度の一覧取得(19903:マスター,19902:エキスパート)
    :param user_id: ユーザーid
    :param music_difficulty: 難易度(masterとか)
    :return json_data: 各難易度の楽曲の情報
    """
    url = 'https://chunithm-net.com/ChuniNet/GetUserMusicApi'
    parm = {"level": music_difficulty, "userId": user_id}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return None
    json_data = re.json()
    return json_data

#ユーザーデータの詳細取得
def Get_UserData(userId):
    url = 'https://chunithm-net.com/ChuniNet/GetUserInfoApi'
    parm = {'userId':userId,'friendCode':0,'fileLevel':1}
    re = requests.post(url,data=json.dumps(parm))
    if re is None:
        return None
    Json = re.json()
    return Json

#直近50曲の取得
def Get_PlayLog(userId):
    url = 'https://chunithm-net.com/ChuniNet/GetUserPlaylogApi'
    parm = {"userId":userId}
    re = requests.post(url,data=json.dumps(parm))
    if re is None:
        return None
    Json = re.json()
    return Json

#自分のフレンドコード取得
def Get_FriendCode(userId):
    url = 'https://chunithm-net.com/ChuniNet/GetUserFriendlistApi'
    parm = {'userId':userId,"state":4}
    re = requests.post(url,data=json.dumps(parm))
    if re is None:
        return None
    Json = re.json()
    if Json is None:
        return None
    return Json.get('friendCode')

#楽曲のジャンルの取得
def Get_Genre(userId,Genre,Level=None):
    if Level:
        url = 'https://chunithm-net.com/ChuniNet/GetUserMusicApi'
        parm = {'userId':userId,'level':'1'+str(Genre)+'0'+str(Level)}
        re = requests.post(url,data=json.dumps(parm))
        if re is None:
            return None
        Json = re.json()
        if Json is None:
            return None
        return Json.get('genreList')
    else:
        url = 'https://chunithm-net.com/ChuniNet/GetUserMusicApi'
        parm = {'userId':userId,'level':'1'+str(Genre)+'02'}
        re = requests.post(url,data=json.dumps(parm))
        if re is None:
            return None
        Json = re.json()
        if Json is None:
            return None
        ExList = Json.get('genreList')
        url = 'https://chunithm-net.com/ChuniNet/GetUserMusicApi'
        parm = {'userId':userId,'level':'1'+str(Genre)+'03'}
        re = requests.post(url,data=json.dumps(parm))
        if re is None:
            return None
        Json = re.json()
        if Json is None:
            return None
        MasList = Json.get('genreList')
        return ExList,MasList


#Json読み込み
def Load_Json():
    f = open("common/chunithm.json", 'r',encoding='utf8')
    data = json.load(f)
    return data

#スコアからレート
def Score2Rate(Score,BaseRate):
    Rate = 0
    if Score >= 1007500:
        Rate = BaseRate+2
    elif Score >= 1005000:
        Rate = BaseRate +  1.5 + (Score - 1005000) * 10.00 / 50000
    elif Score >= 1000000:
        Rate = BaseRate +  1.0 + (Score - 1000000) *  5.00 / 50000
    elif Score >= 975000:
        Rate = BaseRate +  0.0 + (Score -  975000) *  2.00 / 50000
    elif Score >= 950000:
        Rate = BaseRate -  1.5 + (Score -  950000) *  3.00 / 50000
    elif Score >= 925000:
        Rate = BaseRate -  3.0 + (Score -  925000) *  3.00 / 50000
    elif Score >= 900000:
        Rate = BaseRate -  5.0 + (Score -  900000) *  4.00 / 50000
    elif Score >= 800000:
        Rate = BaseRate -  7.5 + (Score -  800000) *  1.25 / 50000
    elif Score >= 700000:
        Rate = BaseRate -  8.5 + (Score -  700000) *  0.50 / 50000
    elif Score >= 600000:
        Rate = BaseRate -  9.0 + (Score -  600000) *  0.25 / 50000
    elif Score >= 500000:
        Rate = BaseRate - 13.7 + (Score -  500000) *  2.35 / 50000
    else:
        None
    return math.floor(Rate * 100) / 100

#レートからスコア
def Rate2Score(BaseRate, Rate):
    diff = Rate - BaseRate
    if diff  >  2.0:
        return -1
    elif diff ==   2.0:
        return 1007500
    elif diff >=   1.5:
        return math.floor((diff -   1.5) * 50000 / 10.00) + 1005000
    elif diff >=   1.0:
        return math.floor((diff -   1.0) * 50000 /  5.00) + 1000000
    elif diff >=   0.0:
        return math.floor((diff -   0.0) * 50000 /  2.00) +  975000
    elif diff >=  -1.5:
        return math.floor((diff -  -1.5) * 50000 /  3.00) +  950000
    elif diff >=  -3.0:
        return math.floor((diff -  -3.0) * 50000 /  3.00) +  925000
    elif diff >=  -5.0:
        return math.floor((diff -  -5.0) * 50000 /  4.00) +  900000
    elif diff >=  -7.5:
        return math.floor((diff -  -7.5) * 50000 /  1.25) +  800000
    elif diff >=  -8.5:
        return math.floor((diff -  -8.5) * 50000 /  0.50) +  700000
    elif diff >=  -9.0:
        return math.floor((diff -  -9.0) * 50000 /  0.25) +  600000
    elif diff >= -13.7:
        return math.floor((diff - -13.7) * 50000 /  2.35) +  500000
    else:
        return -1

def score_to_rank(Score):
    '''スコアからランクにして返す'''
    if Score >= 1007500:
        return 'sss'
    elif Score >= 1000000:
        return 'ss'
    elif Score >= 975000:
        return 's'
    elif Score >= 950000:
        return 'aaa'
    elif Score >= 925000:
        return 'aa'
    elif Score >= 900000:
        return 'a'
    elif Score >= 800000:
        return 'bbb'
    elif Score >= 700000:
        return 'bb'
    elif Score >= 600000:
        return 'b'
    elif Score >= 500000:
        return 'c'
    elif Score >= 0:
        return 'd'
    else:
        return None

#フラグを立てる
def CountRank(Musics):
    rank = Musics[0]['Rank']
    Musics[0]['Flag'] = rank
    for Music in Musics:
        if rank != Music['Rank']:
            rank = Music['Rank']
    Music['flag'] = rank
    return Musics

#難易度を数え上げる
def CountDiff(Musics):
    diff = Musics[0]['Diff']
    Musics[0]['Flag'] = diff
    for Music in Musics:
        if diff != Music['Diff']:
            diff = Music['Diff']
            Music['flag'] = diff
    return Musics
