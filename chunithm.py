# -*- coding: utf-8 -*-
#! python3
import sqlite3,json,requests,math,os,hashlib
from datetime import datetime

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
	'''譜面定数をデータベースから取得する'''
	#前処理
	def __init__(self):
		self.con = sqlite3.connect("common/chunithm.db")
		self.cur = self.con.cursor()

	#譜面定数を取得する
	def Get_BaseRate(self,musicId,level):
		sql = 'SELECT * FROM Music WHERE "MusicId" = ? AND "Level" = ?'
		self.cur.execute(sql,(musicId,level))
		r = self.cur.fetchall()
		return r[0]

	#ファイル名からMusicIdを取得
	def Get_MusicId(self,FileName):
		sql = 'SELECT * FROM Music WHERE "Image" = ?'
		self.cur.execute(sql,(FileName,))
		r = self.cur.fetchall()
		return r[0][0]

#各ユーザのデーターベース
class UserDataBase:
	'''各ユーザーのデータベースに計算結果を保存する'''
	#前処理	
	def __init__(self,Hash):
		Path = 'user/{}.db'.format(Hash)
		#新規ユーザーかどうか
		if os.path.exists(Path):
			self.con = sqlite3.connect(Path)
			self.cur = self.con.cursor()
		else:
			self.con = sqlite3.connect(Path)
			self.cur = self.con.cursor()
			#新規ユーザーなのでテーブルを作成
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
			self.cur.execute('''
				CREATE TABLE `Rate` (
					`DispRate`	INTEGER,
					`HighestRating`	INTEGER,
					`MaxRate`	INTEGER,
					`BestRate`	INTEGER,
					`RecentRate`	INTEGER,
					`Credits`	INTEGER,
					`ExecuteDate`	TEXT
				);
			''')
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
			self.cur.execute('''
				CREATE TABLE `User` (
					'Id'	INTEGER,
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
					`ReincarnationNum`	INTEGER,
					`FriendCode`	INTEGER,
					`Hash`	TEXT,
					`FinalPlayDate`	TEXT,
					`ExecuteDate`	TEXT,
					PRIMARY KEY(`Id`)
				);
			''')
	
	#ベスト枠を保存する
	def SetBest(self,Best):
		#一度削除してからセットする
		self.cur.execute('DELETE FROM Best')
		sql = 'INSERT INTO Best (MusicId,Level,MusicName,Image,BaseRate,Score,Rate) VALUES (?,?,?,?,?,?,?)'
		for Music in Best:			
			self.cur.execute(sql,(Music['MusicId'],Music['Level'],Music['MusicName'],Music['Image'],Music['BaseRate'],Music['Score'],Music['Rate']))
			self.con.commit()

	#リセント候補枠を保存する
	def SetRecent(self,Recent):
		#一度削除してからを保存する
		self.cur.execute('DELETE FROM Recent')
		sql = 'INSERT INTO Recent (MusicId,Level,MusicName,Image,BaseRate,Score,Rate,PlayDate) VALUES (?,?,?,?,?,?,?,?)'
		for Music in Recent:
			self.cur.execute(sql,(Music['MusicId'],Music['Level'],Music['MusicName'],Music['Image'],Music['BaseRate'],Music['Score'],Music['Rate'],Music['PlayDate']))
			self.con.commit()

	#ユーザー情報を保存する
	def SetUser(self,User):
		sql = 'INSERT INTO User (UserName,Level,TotalPoint,TrophyType,WebLimitDate,characterFileName,FriendCount,`Point`,PlayCount,CharacterLevel,TrophyName,ReincarnationNum,FriendCode,Hash,FinalPlayDate,ExecuteDate) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
		self.cur.execute(sql,(User['UserName'],User['Level'],User['TotalPoint'],User['TrophyType'],User['WebLimitDate'],User['CharacterFileName'],User['FriendCount'],User['Point'],User['PlayCount'],User['CharacterLevel'],User['TrophyName'],User['ReincarnationNum'],User['FriendCode'],User['Hash'],User['FinalPlayDate'],User['ExecuteDate']))
		self.con.commit()

	#レートの推移を保存する
	def SetRate(self,Rate):
		sql = 'INSERT INTO Rate (DispRate,HighestRating,MaxRate,BestRate,RecentRate,Credits,ExecuteDate) VALUES (?,?,?,?,?,?,?)'
		self.cur.execute(sql,(Rate['DispRate'],Rate['HighestRating'],Rate['MaxRate'],Rate['BestRate'],Rate['RecentRate'],Rate['Credits'],Rate['ExecuteDate']))
		self.con.commit()

	#リセント候補枠を読み込む
	def LoadRecent(self):
		self.cur.execute("SELECT * FROM Recent")
		rows = self.cur.fetchall()
		if rows:
			Recent = []
			for row in rows:
				Dic = {
					'MusicId':row[0],
					'Level':row[1],
					'MusicName':row[2],
					'Image':row[3],
					'BaseRate':row[4],					
					'Score':row[5],
					'Rate':row[6],
					'PlayDate':row[7]
				}
				Recent.append(Dic)
			return Recent
		else:
			return None

	#ユーザーデータを読み込む
	def LoadUser(self):
		self.cur.execute('SELECT * FROM User')
		rows = self.cur.fetchall()
		if rows:
			User = []
			for row in rows:
				Dic = {
					'Id':row[0],
					'UserName':row[1],
					'Level':row[2],
					'TotalPoint':row[3],
					'TrophyType':row[4],
					'WebLimitDate':row[5],
					'CharacterFileName':row[6],
					'FriendCount':row[7],
					'Point':row[8],
					'PlayCount':row[9],
					'CharacterLevel':row[10],
					'TrophyName':row[11],
					'ReincarnationNum':row[12],
					'FriendCode':row[13],
					'Hash':row[14],
					'FinalPlayDate':row[15],
					'ExecuteDate':row[16]
				}
				User.append(Dic)
			return User
		else:
			return	None

	#レートの推移を読み込む
	def LoadRate(self):
		self.cur.execute('SELECT * FROM Rate')
		rows = self.cur.fetchall()
		if rows:
			Rate = []
			for row in rows:
				Dic = {
					'DispRate':row[0],
					'HighestRating':row[1],
					'MaxRate':row[2],
					'BestRate':row[3],
					'RecentRate':row[4],
					'Credits':row[5],
					'ExecuteDate':row[6]
				}
				Rate.append(Dic)
			return Rate
		else:
			return None

#管理用のデータベース
class AdminDataBase():
	'''管理用のデータベース'''
	def __init__(self):
		if os.path.exists('admin/admin.db'):
			self.con = sqlite3.connect('admin/admin.db')
			self.cur = self.con.cursor()
		else:
			self.con = sqlite3.connect('admin/admin.db')
			self.cur = self.con.cursor()
			self.cur.execute('''
				CREATE TABLE `User` (
					`UserName`	TEXT,
					`FriendCode`	TEXT,
					`Hash`	TEXT,
					`Credits`	INTEGER,
					`DispRate`	INTEGER,
					`HighestRating`	INTEGER,
					`MaxRate`	INTEGER,
					`BestRate`	INTEGER,
					`RecentRate`	INTEGER
				);
			''')

	#データを保存する
	def SetData(self,Data):
		sql = 'SELECT * FROM User WHERE Hash = ?'
		self.cur.execute(sql,(Data['Hash'],))
		r = self.cur.fetchall()
		if r:
			sql = 'INSERT INTO User (UserName,FriendCode,Hash,Credits,DispRate,HighestRating,MaxRate,BestRate,RecentRate) VALUES (?,?,?,?,?,?,?,?,?)'
			self.cur.execute(sql,(Data['UserName'],Data['FriendCode'],Data['Hash'],Data['Credits'],Data['DispRate'],Data['HighestRating'],Data['MaxRate'],Data['BestRate'],Data['RecentRate']))
			self.con.commit()
		else:
			sql = 'DELETE FROM User WHERE Hash = ?'
			self.cur.execute(sql,(Data['Hash'],))
			sql = 'INSERT INTO User (UserName,FriendCode,Hash,Credits,DispRate,HighestRating,MaxRate,BestRate,RecentRate) VALUES (?,?,?,?,?,?,?,?,?)'
			self.cur.execute(sql,(Data['UserName'],Data['FriendCode'],Data['Hash'],Data['Credits'],Data['DispRate'],Data['HighestRating'],Data['MaxRate'],Data['BestRate'],Data['RecentRate']))
			self.con.commit()

if __name__ == '__main__':
	userId = Get_userId('','')	
	Base = LoadBaseRate()
	FriendCode = int(Get_FriendCode(userId))
	Hash = hashlib.sha256(str(FriendCode).encode('utf8')).hexdigest()
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
							'MusicId':MusicId,
							'Level':Level,
							'MusicName':MusicDetail[2],
							'Image':MusicDetail[3],
							'BaseRate':MusicDetail[4],
							'Rate':Score2Rate(Music['scoreMax'],MusicDetail[4]),
							'Score':Music['scoreMax']
						}
						Musics.append(Dic)
	#ソート
	Best = sorted(Musics,key=lambda x:x["Rate"],reverse=True)
	Rate = {'BestRate':0}
	for Music in Best:
		if i < 30:
			Rate['BestRate'] += Music['Rate']
			if i == 0:
				Rate['MaxBestRate'] =  Music['Rate']
			elif i == 29:
				Rate['MinBestRate'] =  Music['Rate']
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
	DataBase.SetBest(Best)

	#Recent
	Playlog = Get_PlayLog(userId)
	Recent = DataBase.LoadRecent()
	LevelMap = {'master':3,"expert":2,"advance":1,"basic":0}
	FinalPlayDate = Playlog['userPlaylogList'][0]['userPlayDate'][0:-2]
	Musics = []
	for Play in Playlog['userPlaylogList'][0:30]:
		MusicId = Base.Get_MusicId(Play['musicFileName'])
		MusicDetail = Base.Get_BaseRate(MusicId,LevelMap[Play['levelName']])
		if MusicDetail[4] is None:
			continue
		else:
			Dic = {
				'MusicId':MusicId,
				'Level':LevelMap[Play['levelName']],
				'MusicName':MusicDetail[2],
				'Image':MusicDetail[3],
				'BaseRate':MusicDetail[4],
				'Rate':Score2Rate(Play['score'],MusicDetail[4]),
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
		UserData = DataBase.LoadUser()
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
	#データベースに保存
	DataBase.SetRecent(Recent)

	#ユーザーデータ
	UserInfo = Get_UserData(userId)['userInfo']
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
	DataBase.SetUser(User)

	#レート計算
	DispRate = (UserInfo['playerRating'] / 100.0)
	BestRate = (Rate['BestRate'] / 30)
	Rating = {		
		'DispRate':DispRate,
		'HighestRating':(UserInfo['highestRating'] / 100.0),
		'MaxRate':((Rate['BestRate'] + Rate['MaxBestRate'] * 10) / 40),
		'BestRate':BestRate,
		'RecentRate':(DispRate * 40 - BestRate * 30) / 10,
		'Credits':UserInfo['playCount'],
		'ExecuteDate': NowDate
	}
	#データベースに保存
	DataBase.SetRate(Rating)

	Admin = AdminDataBase()
	Data = {
		'UserName':UserInfo['userName'],
		'FriendCode':FriendCode,
		'Hash':Hash,
		'Credits':UserInfo['playCount'],
		'DispRate':DispRate,
		'HighestRating':(UserInfo['highestRating'] / 100.0),
		'MaxRate':((Rate['BestRate'] + Rate['MaxBestRate'] * 10) / 40),
		'BestRate':BestRate,
		'RecentRate':(DispRate * 40 - BestRate * 30) / 10
	}
	Admin.SetData(Data)