# -*- coding: utf-8 -*-
#! python3
import json,requests,math

#ログインしてUserIdを取得
def Get_userId(SegaId,password):
	url = 'https://chunithm-net.com/Login/SegaIdLoginApi'
	parm = {'segaId':SegaId, 'password':password}
	re = requests.post(url,data=json.dumps(parm))
	return str(re.json()['sessionIdList'][0])

#Level11以上のMusicIdのリストを取得
def Get_MusicIdList(userId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserMusicLevelApi'
	MusicIdList = []
	ExList = []
	for Level in range(11,14):
		parm = {'userId':userId,'level':Level}
		re = requests.post(url,data=json.dumps(parm))
		Json = re.json()
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
	Json = json.loads(re.text,'utf-8')
	return Json

#各難易度の一覧取得(19903:マスター,19902:エキスパート)
def Get_DiffList(userId,level):
	url = 'https://chunithm-net.com/ChuniNet/GetUserMusicApi'
	parm = {"level":level,"userId":userId}
	re = requests.post(url,data=json.dumps(parm))
	Json = re.json()
	return Json

#ユーザーデータの詳細取得
def Get_UserData(userId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserInfoApi'
	parm = {'userId':userId,'friendCode':0,'fileLevel':1}
	re = requests.post(url,data=json.dumps(parm))
	Json = re.json()
	return Json

#直近50曲の取得
def Get_PlayLog(userId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserPlaylogApi'
	parm = {"userId":userId}
	re = requests.post(url,data=json.dumps(parm))
	Json = re.json()
	return Json

#自分のフレンドコード取得
def Get_FriendCode(userId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserFriendlistApi'
	parm = {'userId':userId,"state":4}
	re = requests.post(url,data=json.dumps(parm))
	Json = re.json()
	return Json['friendCode']

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
	return math.floor(Rate * 100) / 100

#レートからスコア
def Rate2Score(BaseRate, Rate):
	diff = Rate - BaseRate;
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