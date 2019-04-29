from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime
import json
from .enums import *

def convertTime(t):
	return t.isoformat(' ') #t.strftime('%Y-%m-%d %H:%M:%S')

def timeFromString(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def setUserFromKwargs(kwargs, params):
	user = kwargs.get('user', 0)
	userID = kwargs.get('userID', 0)
	username = kwargs.get('username', '')

	if userID != 0:
			user = int(userID)
	elif username != '':
		user = str(username)

	if user != 0:
		params['u'] = str(user)
		params['type'] = ('string' if type(user) is str else 'id')

# TODO return custom objects instead of json dictionaries
# TODO all methods

class Api:
	BASE = 'https://osu.ppy.sh/api'

	def __init__(self, key):
		self.key = key

	def getUser(self, **kwargs):
		url = self.BASE + '/get_user'
		mode = kwargs.get('mode', MODE_STD)
		eventDays = kwargs.get('eventDays', 31)

		params = {'k':self.key}
		setUserFromKwargs(kwargs, params)

		if mode != MODE_STD:
			params['m'] = str(mode)

		params['eventDays'] = str(eventDays)

		return json.loads(urlopen(url+'?'+urlencode(params)).read().decode('utf-8'))

	def getScores(self, **kwargs):
		url = self.BASE + '/get_scores'

		beatmap = kwargs.get('beatmap')
		mode = kwargs.get('mode', MODE_STD)
		limit = kwargs.get('limit', 100)

		params = {'k':self.key}
		setUserFromKwargs(kwargs, params)
		if mode != MODE_STD:
			params['m'] = str(mode)

		params['limit'] = str(limit)
		params['b'] = str(beatmap)

		return json.loads(urlopen(url+'?'+urlencode(params)).read().decode('utf-8'))

	def getBeatmaps(self, **kwargs):
		since=kwargs.get('since', None)
		until=kwargs.get('until', datetime.utcnow())
		beatmapset = kwargs.get('beatmapset', 0)
		beatmap = kwargs.get('beatmap', 0)
		mode = kwargs.get('mode', -1)
		includeConverts = kwargs.get('includeConverts', False)
		mapHash = kwargs.get('mapHash', '')
		limit = kwargs.get('limit', 0)

		url = self.BASE + '/get_beatmaps'
		params = {'k':self.key}

		if beatmapset != 0:
			params['s'] = str(beatmapset)

		if beatmap != 0:
			params['s'] = str(beatmap)
		
		setUserFromKwargs(kwargs, params)

		if mode >= MODE_STD and mode <= MODE_LAST:
			params['m'] = str(mode)

		if includeConverts:
			params['a'] = '1'

		if mapHash:
			params['h'] = 'h'

		if since is None:
			if limit != 0:
				params['limit'] = limit
			return json.loads(urlopen(url, urlencode(params).encode('utf-8')).read().decode('utf-8'))

		if limit == 0:
			limit = 0xFFFFFFFF
		ret = []
		params['limit'] = 500

		while since < until:
			params['since'] = convertTime(since)
			newData = json.loads(urlopen(url, urlencode(params).encode('utf-8')).read().decode('utf-8'))

			shouldBreak = False

			for b in newData:
				if timeFromString(b['approved_date']) <= until and len(ret) < limit:
					ret.append(b)
				else:
					shouldBreak = True
					break


			if len(newData) < 500 or shouldBreak:
				break
			else:
				since = timeFromString(newData[-1]['approved_date'])

		beatmapsAll = {}
		for b in ret:
			beatmapsAll[f'{b["beatmap_id"]}|{b["beatmapset_id"]}'] = b
		ret = [*beatmapsAll.values()]

		return ret




class ApiV2:
	pass