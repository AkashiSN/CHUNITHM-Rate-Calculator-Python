import sqlite3
from common import Function as Func

if __name__ == '__main__':
	userId = Func.Get_userId('akashisn','vAw7ujeheta6efrA')
	ExList,MusicIdList = Func.Get_MusicIdList(userId)
	Base = Func.Load_Json()
	SQL = 'INSERT INTO Music (MusicId, Level, MusicName, Image, BaseRate, Air) VALUES (?,?,?,?,?,?);'	
	con = sqlite3.connect('common/chunithm.db')
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
		music = Func.Get_BestScore(userId,MusicID)
		MusicImage = music['musicFileName']
		MusicName = music['musicName']
		BaseRate = None
		if str(MusicID) in Base:
			BaseRate = Base[str(MusicID)]['BaseRate']['mas']
		cur.execute(SQL,(MusicID,3,MusicName,MusicImage,BaseRate,None))
	for MusicID in ExList:
		music = Func.Get_BestScore(userId,MusicID)
		MusicImage = music['musicFileName']
		MusicName = music['musicName']
		BaseRate = None
		if str(MusicID) in Base['ExpertExist']:
			BaseRate = Base[str(MusicID)]['BaseRate']['ex']
		cur.execute(SQL,(MusicID,2,MusicName,MusicImage,BaseRate,None))

	con.commit()
	con.close()