# coding: utf-8
#!/usr/bin/env python3
import sqlite3,json,requests

#Json読み込み
def Load_Json():
	f = open("/root/CHUNITHM/chunithm.json")
	data = json.load(f)
	return data

#ログインしてUserIDを取得
def Get_userId(SegaId,password):
	url = 'https://chunithm-net.com/Login/SegaIdLoginApi'
	parm = {'segaId': '{}'.format(SegaId), 'password': '{}'.format(password)}
	re = requests.post(url,data=json.dumps(parm))
	return re.json()['sessionIdList'][0]

#Level11以上のMusicIDのリストを取得
def Get_MusicIdList(userId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserMusicLevelApi'
	MusicIdList = []
	ExList = []
	for Level in range(11,14):
		parm = {'userId':'{}'.format(userId),'level':'{}'.format(Level)}
		re = requests.post(url,data=json.dumps(parm))
		Json = re.json()
		MusicIdList += Json['levelList']
		MusicIdList += Json['levelPlusList']
		for Id,dif in Json['difLevelMap'].items():
			if dif == 2:
				ExList.append(int(Id))
	MusicIdList = list(set(MusicIdList))
	ExList = list(set(ExList))
	return MusicIdList,ExList

#楽曲の詳細情報を取得
def BestScore_get(userId,musicId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserMusicDetailApi'
	parm = {'userId':'{}'.format(userId),'musicId':'{}'.format(musicId)}
	re = requests.post(url,data=json.dumps(parm))
	Json = json.loads(re.text,'utf-8')
	return Json


if __name__ == '__main__':
	userId = Get_userId('','')
	MusicIdList,ExList = Get_MusicIdList(userId)
	Base = Load_Json()
	SQL = 'INSERT INTO Music (MusicId, Level, MusicName, Image, BaseRate, Air) VALUES (?,?,?,?,?,?);'	

	con = sqlite3.connect('./chunithm.db')
	cur = con.cursor()
	cur.execute("""CREATE TABLE "Music" (
		`MusicID`	INTEGER,
		`Level`	INTEGER,
		`MusicName`	TEXT,
		`Image`	TEXT,
		`BaseRate`	INTEGER DEFAULT null,
		`Air`	INTEGER DEFAULT null
	);""")

	for MusicID in MusicIdList:
		music = BestScore_get(userId,MusicID)
		MusicImage = music['musicFileName']
		MusicName = music['musicName']
		BaseRate = None
		if str(MusicID) in Base:
			BaseRate = Base[str(MusicID)]['BaseRate']['mas']
		cur.execute(SQL,(MusicID,3,MusicName,MusicImage,BaseRate,None))
	for MusicID in ExList:
		music = BestScore_get(userId,MusicID)
		MusicImage = music['musicFileName']
		MusicName = music['musicName']
		BaseRate = None
		if str(MusicID) in Base['ExpertExist']:
			BaseRate = Base[str(MusicID)]['BaseRate']['ex']
		cur.execute(SQL,(MusicID,2,MusicName,MusicImage,BaseRate,None))

	con.commit()
	con.close()