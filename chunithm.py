#!/usr/bin/env python3
import hashlib,math,sys
from datetime import datetime
from common import Function as Func
from common import DataBase as DB
from pprint import pprint

#レートを計算してデータベースに保存する
def CalcRate(userId):
    '''レートを計算してデータベースに保存する'''

    Base = DB.LoadBaseRate()
    FriendCode = Func.Get_FriendCode(userId)
    if FriendCode is None:
        return None

    Hash = hashlib.sha256(str(FriendCode).encode('utf8')).hexdigest()

    Rating = {}
    DataBase = DB.UserDataBase(Hash)

    #Best枠について
    MusicIdList = Func.Get_MusicIdList(userId) #MusicIdのリストの取得
    if MusicIdList is None:
        return None
    Musics = []
    i = 0
    for Level in range(2,4):
        MusicBestScore = Func.Get_DiffList(userId,"1990"+str(Level)) #エキスパート(19902)とマスター(19903)の曲別最大スコアのリストの取得
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
                            'Rate':Func.Score2Rate(Music['scoreMax'],MusicDetail['BaseRate']),
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
        if len(Recent) > 10:
            UserData = DataBase.LoadUser()
            try:
                if UserData[-1]['FinalPlayDate'] is None:
                    return None
            except Exception as e:
                return None
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
    RecentRates = 0
    i = 0
    for Music in Recent:
        if i < 10:
            RecentRates += Music['Rate']
            i += 1

    #データベースに保存
    DataBase.SetRecent(Recent)

    #ユーザーデータ
    UserInfo = Func.Get_UserData(userId)
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
    DataBase.SetUser(User)

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
#    データベースに保存
    DataBase.SetRate(Rating)

    Admin = DB.AdminDataBase()
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
    DataBase = DB.UserDataBase(Hash)
    Best = DataBase.LoadBest()
    User = DataBase.LoadUser()
    Rate = DataBase.LoadRate()
    return Best,User,Rate

#Recent枠の時の表示
def DispRecent(Hash):
    DataBase = DB.UserDataBase(Hash)
    Recent = DataBase.LoadRecent()
    User = DataBase.LoadUser()
    Rate = DataBase.LoadRate()
    return Recent,User,Rate

#Graphの表示
def DispGraph(Hash):
    DataBase = DB.UserDataBase(Hash)
    Rate = DataBase.LoadRate()
    User = DataBase.LoadUser()
    return User,Rate

#Toolの表示
def DispTools(Hash):
    DataBase = DB.UserDataBase(Hash)
    DataBase = DB.UserDataBase(Hash)
    Rate = DataBase.LoadRate()
    User = DataBase.LoadUser()
    return User,Rate

#譜面定数の確認
def CheckMusic(userId):
    MusicIdList = Func.Get_MusicIdList(userId)
    DataBase = DB.LoadBaseRate()
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
                        'Level':level,
                        'BaseRate':BaseRate
                    }
                    ExistMusicList.append(Dic)
                    continue            
            Music = Func.Get_BestScore(userId,MusicId)
            Dic = {
                'MusicId':MusicId,
                'MusicName':Music['musicName'],
                'MusicImage':Music['musicFileName'],
                'ArtistName':Music['artistName'],
                'Level':level,
                'BaseRate':None
            }
            NoneMusicList.append(Dic)
    return NoneMusicList,ExistMusicList

#譜面定数の更新
def SetMusic(UserId,MusicId,Level,BaseRate):
    Music = Func.Get_BestScore(UserId, MusicId)
    DataBase = DB.LoadBaseRate()
    Dic = {
        'MusicId':MusicId,
        'Level':Level,
        'MusicName':Music['musicName'],
        'Image':Music['musicFileName'],
        'BaseRate':BaseRate
    }
    DataBase.SetMusic(Dic)