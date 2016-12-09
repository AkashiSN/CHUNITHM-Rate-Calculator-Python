# -*- coding: utf-8 -*-
import sqlite3,json,requests,math,os,hashlib

#ログインしてUserIDを取得
def Get_userId(SegaId,password):
	url = 'https://chunithm-net.com/Login/SegaIdLoginApi'
	parm = {'segaId':SegaId, 'password':password}
	re = requests.post(url,data=json.dumps(parm))
	return str(re.json()['sessionIdList'][0])

#Level11以上のMusicIDのリストを取得
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

#譜面定数取得
class LoadBaseRate:
	def __init__(self):
		self.con = sqlite3.connect("./chunithm.db")
		self.cur = self.con.cursor()
	def Get_BaseRate(self,musicId,level):
		sql = 'SELECT * FROM Music WHERE "MusicID" = ? AND "Level" = ?'
		self.cur.execute(sql,(musicId,level))
		r = self.cur.fetchall()
		return r[0]
	def Get_MusicId(self,FileName):
		sql = 'SELECT * FROM Music WHERE "Image" = ?'
		self.cur.execute(sql,(FileName,))
		r = self.cur.fetchall()
		return r[0][0]

#各ユーザのデーターベース
class UserDataBase:
	
	def __init__(self,Hash):
		Path = './user/{}.db'.format(Hash)
		if os.path.exists(Path):
			self.con = sqlite3.connect(Path)
			self.cur = self.con.cursor()
		else:
			self.con = sqlite3.connect(Path)
			self.cur = self.con.cursor()
			self.CreateTable_User()
			self.CreateTable_Best()
			self.CreateTable_Recent()
			self.CreateTable_Rate()

	def CreateTable_Best(self):
		self.cur.execute('''
			CREATE TABLE `Best` (
				`MusicId`	INTEGER,
				`Level`	INTEGER,
				`MusicName`	TEXT,
				`Image`	TEXT,
				`BaseRate`	INTEGER,
				`Score`	INTEGER,
				`Rate`	INTEGER
			);
		''')
	def CreateTable_Rate(self):
		self.cur.execute('''
			CREATE TABLE `Rate` (
				`DispRate`	INTEGER,
				`HighestRating`	INTEGER,
				`MaxRate`	INTEGER,
				`BestRate`	INTEGER,
				`RecentRate`	INTEGER
			);
		''')
	def CreateTable_Recent(self):
		self.cur.execute('''
			CREATE TABLE `Recent` (
				`MusicId`	INTEGER,
				`Level`	INTEGER,
				`MusicName`	TEXT,
				`Image`	TEXT,
				`BaseRate`	INTEGER,
				`Score`	INTEGER,
				`Rate`	INTEGER,
				`PlayDate` TEXT
			);
		''')
	def CreateTable_User(self):
		self.cur.execute('''
			CREATE TABLE `User` (
				`UserName`	TEXT,
				`Level`	INTEGER,
				`TotalPoint`	INTEGER,
				`TrophyType`	INTEGER,
				`WebLimitDate`	TEXT,
				`CharacterFileName`	TEXT,
				`FriendCount`	INTEGER,
				`Point`	INTEGER,
				`PlayCount`	INTEGER,
				`CharacterLevel`	INTEGER,
				`TrophyName`	TEXT,
				`ReincarnationNum`	INTEGER
			);
		''')
	def SetBest(self,Best):
		self.cur.execute('DELETE FROM Best')
		sql = 'INSERT INTO Best (MusicId,Level,MusicName,Image,BaseRate,Score,Rate) VALUES (?,?,?,?,?,?,?)'
		for Music in Best:			
			self.cur.execute(sql,(Music['MusicID'],Music['Level'],Music['MusicName'],Music['Image'],Music['BaseRate'],Music['Score'],Music['BestRate']))
			self.con.commit()

if __name__ == '__main__':
	userId = Get_userId('akashisn','phamEfrahEf5Huw')	
	Base = LoadBaseRate()
	FriendCode = int(Get_FriendCode(userId))
	#Hash = hashlib.sha256(bytes(FriendCode)).hexdigest()
	Hash = 'bdbc5af0d01b1b28716da405a166381571d0c003628875c15e099a773477611f'
	Rating = {}
	DataBase = UserDataBase(Hash)

	#Best
	MusicIdList = Get_MusicIdList(userId)
	Musics = []
	i = 0
	for Level in range(2,4):
		MusicBestScore = Get_DiffList(userId,"1990"+str(Level))
		for MusicId in MusicIdList[Level-2]:
			for Music in MusicBestScore['userMusicList']:
				if Music['musicId'] == MusicId:
					MusicDetail = Base.Get_BaseRate(MusicId,Level)
					if MusicDetail[4] is None:
						break
					else:
						Dic = {
							'MusicID':MusicId,
							'Level':Level,
							'MusicName':MusicDetail[2],
							'Image':MusicDetail[3],
							'BaseRate':MusicDetail[4],
							'BestRate':Score2Rate(Music['scoreMax'],MusicDetail[4]),
							'Score':Music['scoreMax']
						}
						Musics.append(Dic)
	#ソート
	Best = sorted(Musics,key=lambda x:x["BestRate"],reverse=True)
	Rate = {'BestRate':0}
	for Music in Best:
		if i < 30:
			Rate['BestRate'] += Music['BestRate']
			if i == 0:
				Rate['MaxBestRate'] =  Music['BestRate']
			elif i == 29:
				Rate['MinBestRate'] =  Music['BestRate']
		else:
			if Music['Score'] >= 1007500:
				Music['MaxScore'] = None
			else:
				MaxScore = Rate2Score(Music['BaseRate'],Rate['MinBestRate'])
				if MaxScore <= 1007500 and MaxScore > 0:
					Music['MaxScore'] = MaxScore
				else:
					Music['MaxScore'] = None
		i+=1

	#データーベースに保存
	DataBase.SetBest(Best[::-1])

	# #Recent
	# Playlog = Get_PlayLog(userId)
	# LevelMap = {'master':3,"expert":2,"advance":1,"basic":0}
	# Musics = []
	# for Play in Playlog['userPlaylogList']:
	# 	MusicId = Base.Get_MusicId(Play['musicFileName'])
	# 	MusicDetail = Base.Get_BaseRate(MusicId,LevelMap[Play['levelName']])
	# 	if MusicDetail[4] is None:
	# 		break
	# 	else:
	# 		Dic = {
	# 			'MusicID':MusicId,
	# 			'Level':LevelMap[Play['levelName']],
	# 			'MusicName':MusicDetail[2],
	# 			'Image':MusicDetail[3],
	# 			'BaseRate':MusicDetail[4],
	# 			'BestRate':Score2Rate(Play['score'],MusicDetail[4]),
	# 			'Score':Play['score'],
	# 			'PlayDate':Play['userPlayDate']
	# 		}
	# 		Musics.append(Dic)

	#User
	tmp = Get_UserData(userId)
	UserInfo = tmp['userInfo']

	User = {
		'TotalPoint':UserInfo['totalPoint'],
		'TrophyType':UserInfo['trophyType'],
		'WebLimitDate':UserInfo['webLimitDate'],
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
		'Hash':Hash
	}

	DispRate = (UserInfo['playerRating'] / 100.0)
	BestRate = (Rate['BestRate'] / 30)

	Rating = {
		'HighestRating':(UserInfo['highestRating'] / 100.0),
		'DispRate':DispRate,
		'MaxRate':((Rate['BestRate'] + Rate['MaxBestRate'] * 10) / 40),
		'BestRate':BestRate,
		'RecentRate':(DispRate * 40 - BestRate * 30)
	}
	
	User['Rating'] = Rating