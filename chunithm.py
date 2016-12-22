# -*- coding: utf-8 -*-
#! python3
import hashlib
from datetime import datetime
from common import Function as Func
from common import DataBase as DB

def CalcRate(SegaId,password):
	userId = Func.Get_userId(SegaId,password)	
	Base = DB.LoadBaseRate()
	FriendCode = int(Func.Get_FriendCode(userId))
	Hash = hashlib.sha256(str(FriendCode).encode('utf8')).hexdigest()
	Rating = {}
	DataBase = DB.UserDataBase(Hash)

	#Best
	MusicIdList = Func.Get_MusicIdList(userId)
	Musics = []
	i = 0
	for Level in range(2,4):
		MusicBestScore = Func.Get_DiffList(userId,"1990"+str(Level))
		for MusicId in MusicIdList[Level-2]:
			for Music in MusicBestScore['userMusicList']:
				if Music['musicId'] == MusicId:
					MusicDetail = Base.Get_BaseRate(MusicId,Level)
					if MusicDetail['BaseRate'] is None:
						break
					else:
						Dic = {
							'MusicId':MusicId,
							'Level':Level,
							'MusicName':MusicDetail['MusicName'],
							'Image':MusicDetail['Image'],
							'BaseRate':MusicDetail['BaseRate'],
							'Rate':Func.Score2Rate(Music['scoreMax'],MusicDetail['BaseRate']),
							'Score':Music['scoreMax']
						}
						Musics.append(Dic)
	#ソート
	Best = sorted(Musics,key=lambda x:x["Rate"],reverse=True)
	Rate = {'BestRate':0}
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
				MaxScore = Func.Rate2Score(Music['BaseRate'],Rate['MinBestRate'])
				if MaxScore <= 1007500 and MaxScore > 0:
					Music['MaxScore'] = MaxScore
				else:
					Music['MaxScore'] = None
		i+=1

	#データーベースに保存
	DataBase.SetBest(Best)

	#Recent
	Playlog = Func.Get_PlayLog(userId)
	Recent = DataBase.LoadRecent()
	LevelMap = {'master':3,"expert":2,"advance":1,"basic":0}
	FinalPlayDate = Playlog['userPlaylogList'][0]['userPlayDate'][0:-2]
	Musics = []
	for Play in Playlog['userPlaylogList'][0:30]:
		MusicId = Base.Get_MusicId(Play['musicFileName'])
		MusicDetail = Base.Get_BaseRate(MusicId,LevelMap[Play['levelName']])
		if MusicDetail['BaseRate'] is None:
			continue
		else:
			Dic = {
				'MusicId':MusicId,
				'Level':LevelMap[Play['levelName']],
				'MusicName':MusicDetail['MusicName'],
				'Image':MusicDetail['Image'],
				'BaseRate':MusicDetail['BaseRate'],
				'Rate':Func.Score2Rate(Play['score'],MusicDetail['BaseRate']),
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
	UserInfo = Func.Get_UserData(userId)['userInfo']
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

	Admin = DB.AdminDataBase()
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
	