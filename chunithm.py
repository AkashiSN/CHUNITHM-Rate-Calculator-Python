#!/usr/bin/env python3

import requests,json

#ログインしてUserIDを取得
def Get_UserId(SegaId,password):
	url = 'https://chunithm-net.com/Login/SegaIdLoginApi'
	parm = {'segaId': '{}'.format(SegaId), 'password': '{}'.format(password)}
	re = requests.post(url,data=json.dumps(parm))
	return re.json()['sessionIdList'][0]

#Level11以上のMusicIDのリストを取得
def Get_MusicIdList(UserId):
	url = 'https://chunithm-net.com/ChuniNet/GetUserMusicLevelApi'
	MusicIdList = []
	ExList = []
	for Level in range(11,14):
		parm = {'userId':'{}'.format(UserId),'level':'{}'.format(Level)}
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

UserId = Get_UserId('akashisn','3adazatUja28erAp')
MusicIdList,ExList = Get_MusicIdList(UserId)

print "Content-Type: text/plain;charset=utf-8"
print
print(MusicIdList)
print(ExList)