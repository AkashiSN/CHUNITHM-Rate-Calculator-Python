#!/usr/bin/env python3

import json
import requests
import math
from flask import render_template
from flask import abort


def init_errors(app):
    """
    エラーバンドルの設定
    :param app: アプリケーション
    :return: エラー画面
    """
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(405)
    def gateway_error(error):
        return render_template("errors/405.html"), 405

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html"), 400

    @app.errorhandler(500)
    def general_error(error):
        return render_template("errors/500.html"), 500


def login_time_out():
    """
    ログインセッションが切れたときのエラー画面
    :return:
    """
    return render_template("errors/440.html")


def extraction_user_id(post_data):
    """
    ポストデータからuser_idを抽出
    :param post_data: ポストデータ
    :return: ユーザーid
    """
    tmp = post_data.split(";")
    for tmp1 in tmp:
        if "userId" in tmp1:
            return tmp1.split("=")[1]
    return abort(400)


def fetch_user_id(sega_id, password):
    """
    ログインしてUserIdを取得
    :param sega_id: セガid
    :param password: パスワード
    :return: ユーザーid
    """
    url = "https://chunithm-net.com/Login/SegaIdLoginApi"
    parm = {"segaId": sega_id, "password": password}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return abort(400)
    else:
        return str(re.json()["sessionIdList"][0])


def fetch_user_friend_code(user_id):
    """
    自分のフレンドコード取得
    :param user_id:
    :return:
    """
    url = "https://chunithm-net.com/ChuniNet/GetUserFriendlistApi"
    parm = {"userId": user_id, "state": 4}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return abort(400)
    json_data = re.json()
    if json_data is None:
        render_template("errors/440.html")
    return json_data.get("friendCode")


def fetch_music_id_list(user_id):
    """
    music_level11以上のmusic_idのリストを取得
    :param user_id: ユーザーid
    :return music_id_list: 難易度master楽曲idのリスト
    :return expert_music_id_list: 難易度expert楽曲idのリスト
    """
    url = "https://chunithm-net.com/ChuniNet/GetUserMusicLevelApi"
    music_id_list = []
    expert_music_id_list = []
    for music_level in range(11, 14):
        parm = {"userId": user_id, "level": music_level}
        re = requests.post(url, data=json.dumps(parm))
        if re is None:
            return abort(400)
        json_data = re.json()
        if json_data is None:
            return abort(400)
        music_id_list += json_data["levelList"]
        music_id_list += json_data["levelPlusList"]
        for Id, dif in json_data["difLevelMap"].items():
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
    :return: 取得したデータ
    """
    url = "https://chunithm-net.com/ChuniNet/GetUserMusicDetailApi"
    parm = {"userId": user_id, "musicId": music_id}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return abort(400)
    json_data = json.loads(re.text, "utf-8")
    return json_data


#
def fetch_difficulty_list(user_id, music_difficulty):
    """
    各難易度の一覧取得(19903:マスター,19902:エキスパート)
    :param user_id: ユーザーid
    :param music_difficulty: 難易度(masterとか)
    :return: 各難易度の楽曲の情報
    """
    url = "https://chunithm-net.com/ChuniNet/GetUserMusicApi"
    parm = {"level": music_difficulty, "userId": user_id}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return abort(400)
    json_data = re.json()
    return json_data


def fetch_user_data(user_id):
    """
    ユーザーデータの詳細取得
    :param user_id: ユーザーid
    :return: ユーザーの詳細情報
    """
    url = "https://chunithm-net.com/ChuniNet/GetUserInfoApi"
    parm = {"userId": user_id, "friendCode": 0, "fileLevel": 1}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return abort(400)
    json_data = re.json()
    return json_data


def fetch_play_log(user_id):
    """
    直近50曲の取得
    :param user_id: ユーザーid
    :return: 直近50曲のリスト
    """
    url = "https://chunithm-net.com/ChuniNet/GetUserPlaylogApi"
    parm = {"userId": user_id}
    re = requests.post(url, data=json.dumps(parm))
    if re is None:
        return abort(400)
    json_data = re.json()
    return json_data


def fetch_genre(user_id, genre, level=None):
    """
    楽曲のジャンルの取得
    :param user_id:
    :param genre:
    :param level:
    :return:
    """
    if level:
        url = "https://chunithm-net.com/ChuniNet/GetUserMusicApi"
        parm = {"userId": user_id, "level": "1"+str(genre)+"0"+str(level)}
        re = requests.post(url, data=json.dumps(parm))
        if re is None:
            return abort(400)
        json_data = re.json()
        if json_data is None:
            return abort(400)
        return json_data.get("genreList")
    else:
        url = "https://chunithm-net.com/ChuniNet/GetUserMusicApi"
        parm = {"userId": user_id, "level": "1"+str(genre)+"02"}
        re = requests.post(url, data=json.dumps(parm))
        if re is None:
            return abort(400)
        json_data = re.json()
        if json_data is None:
            return abort(400)
        expert_music_id_list = json_data.get("genreList")
        url = "https://chunithm-net.com/ChuniNet/GetUserMusicApi"
        parm = {"userId": user_id, "level": "1"+str(genre)+"03"}
        re = requests.post(url, data=json.dumps(parm))
        if re is None:
            return abort(400)
        json_data = re.json()
        if json_data is None:
            return abort(400)
        music_id_list = json_data.get("genreList")
        return expert_music_id_list, music_id_list


def load_json():
    """
    楽曲情報の読み込み
    :return: 楽曲情報
    """
    f = open("common/chunithm.json", "r", encoding="utf8")
    data = json.load(f)
    return data


def score_to_rate(music_score, music_base_rate):
    """
    スコアからレート
    :param music_score: 楽曲のスコア
    :param music_base_rate: 楽曲の譜面定数
    :return: 楽曲のレート
    """
    if music_score >= 1007500:
        music_rate = music_base_rate+2
    elif music_score >= 1005000:
        music_rate = music_base_rate + 1.5 + (music_score - 1005000) * 10.00 / 50000
    elif music_score >= 1000000:
        music_rate = music_base_rate + 1.0 + (music_score - 1000000) * 5.00 / 50000
    elif music_score >= 975000:
        music_rate = music_base_rate + 0.0 + (music_score - 975000) * 2.00 / 50000
    elif music_score >= 950000:
        music_rate = music_base_rate - 1.5 + (music_score - 950000) * 3.00 / 50000
    elif music_score >= 925000:
        music_rate = music_base_rate - 3.0 + (music_score - 925000) * 3.00 / 50000
    elif music_score >= 900000:
        music_rate = music_base_rate - 5.0 + (music_score - 900000) * 4.00 / 50000
    elif music_score >= 800000:
        music_rate = music_base_rate - 7.5 + (music_score - 800000) * 1.25 / 50000
    elif music_score >= 700000:
        music_rate = music_base_rate - 8.5 + (music_score - 700000) * 0.50 / 50000
    elif music_score >= 600000:
        music_rate = music_base_rate - 9.0 + (music_score - 600000) * 0.25 / 50000
    elif music_score >= 500000:
        music_rate = music_base_rate - 13.7 + (music_score - 500000) * 2.35 / 50000
    else:
        music_rate = 0
    return math.floor(music_rate * 100) / 100


def rate_to_score(music_base_rate, music_rate):
    """    レートからスコア
    :param music_base_rate: 楽曲の譜面定数
    :param music_rate: 楽曲のレート
    :return: 楽曲のスコア
    """
    diff = music_rate - music_base_rate
    if diff > 2.0:
        return -1
    elif diff == 2.0:
        return 1007500
    elif diff >= 1.5:
        return math.floor((diff - 1.5) * 50000 / 10.00) + 1005000
    elif diff >= 1.0:
        return math.floor((diff - 1.0) * 50000 / 5.00) + 1000000
    elif diff >= 0.0:
        return math.floor((diff - 0.0) * 50000 / 2.00) + 975000
    elif diff >= -1.5:
        return math.floor((diff - -1.5) * 50000 / 3.00) + 950000
    elif diff >= -3.0:
        return math.floor((diff - -3.0) * 50000 / 3.00) + 925000
    elif diff >= -5.0:
        return math.floor((diff - -5.0) * 50000 / 4.00) + 900000
    elif diff >= -7.5:
        return math.floor((diff - -7.5) * 50000 / 1.25) + 800000
    elif diff >= -8.5:
        return math.floor((diff - -8.5) * 50000 / 0.50) + 700000
    elif diff >= -9.0:
        return math.floor((diff - -9.0) * 50000 / 0.25) + 600000
    elif diff >= -13.7:
        return math.floor((diff - -13.7) * 50000 / 2.35) + 500000
    else:
        return -1


def score_to_rank(music_score):
    """
    スコアからランクにして返す
    :param music_score: 楽曲のスコア
    :return: 楽曲のランク
    """
    if music_score >= 1007500:
        return "sss"
    elif music_score >= 1000000:
        return "ss"
    elif music_score >= 975000:
        return "s"
    elif music_score >= 950000:
        return "aaa"
    elif music_score >= 925000:
        return "aa"
    elif music_score >= 900000:
        return "a"
    elif music_score >= 800000:
        return "bbb"
    elif music_score >= 700000:
        return "bb"
    elif music_score >= 600000:
        return "b"
    elif music_score >= 500000:
        return "c"
    elif music_score >= 0:
        return "d"
    else:
        return None


def count_rank(musics):
    """
    フラグを立てる
    :param musics: 楽曲のリスト
    :return: フラグを立てた楽曲のリスト
    """
    rank = musics[0]["Rank"]
    musics[0]["Flag"] = rank
    for music in musics:
        if rank != music["Rank"]:
            rank = music["Rank"]
    musics["flag"] = rank
    return musics


def count_diff(musics):
    """
    難易度を数え上げる
    :param musics: 楽曲のリスト
    :return: 難易度を加えた楽曲のリスト
    """
    diff = musics[0]["Diff"]
    musics[0]["Flag"] = diff
    for music in musics:
        if diff != music["Diff"]:
            diff = music["Diff"]
            music["flag"] = diff
    return musics
