#!/usr/bin/env python3
import json,requests,math

#ポストデータからUserIdを取得
def userId_Get(userId):
    tmp = userId.split(';')
    for tmp1 in tmp:
        if 'userId' in tmp1:
            return tmp1.split('=')[1]
    return None

#ログインしてUserIdを取得
def Get_userId(SegaId,password):
    url = 'https://chunithm-net.com/Login/SegaIdLoginApi'
    parm = {'segaId':SegaId, 'password':password}
    re = requests.post(url,data=json.dumps(parm))
    if re is None:
        return None
    else:
        return str(re.json()['sessionIdList'][0])

#Level11以上のMusicIdのリストを取得
def Get_MusicIdList(userId):
    url = 'https://chunithm-net.com/ChuniNet/GetUserMusicLevelApi'
    MusicIdList = []
    ExList = []
    for Level in range(11,15):
        parm = {'userId':userId,'level':Level}
        re = requests.post(url,data=json.dumps(parm))
        if re is None:
            return None
        Json = re.json()
        if Json is None:
            return None
        MusicIdList += Json['levelList']
        MusicIdList += Json['levelPlusList']
        for Id,dif in Json['difLevelMap'].items():
            if dif == 2:
                ExList.append(int(Id))
    MusicIdList = list(set(MusicIdList))
    ExList = list(set(ExList))
    return ExList,MusicIdList

#楽曲の詳細情報を取得
def Get_BestScore(userId,musicId):
    url = 'https://chunithm-net.com/ChuniNet/GetUserMusicDetailApi'
    parm = {'userId':userId,'musicId':musicId}
    re = requests.post(url,data=json.dumps(parm))
    if re is None:
        return None
    Json = json.loads(re.text,'utf-8')
    return Json

#各難易度の一覧取得(19903:マスター,19902:エキスパート)
def Get_DiffList(userId,level):
    url = 'https://chunithm-net.com/ChuniNet/GetUserMusicApi'
    parm = {"level":level,"userId":userId}
    re = requests.post(url,data=json.dumps(parm))
    if re is None:
        return None
    Json = re.json()
    return Json

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

#スコアからランク
def Score2Rank(Score):
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

#譜面定数から難易度
def BaseRate2Diff(BaseRate):
    if BaseRate >= 14:
        return '14'
    if BaseRate >= 13.7:
        return '13+'
    if BaseRate >= 13:
        return '13'
    if BaseRate >= 12.7:
        return '12+'
    if BaseRate >= 12:
        return '12'
    if BaseRate >= 11.7:
        return '11+'
    if BaseRate >= 11:
        return '11'

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
