#!/usr/bin/python3
from datetime import datetime
from osu import *
import json, tqdm, os, sys, argparse

parser = argparse.ArgumentParser(description='Add osu! collections filtered by mods and accuracy')

def parseMode(s):
	if type(s) is int:
		return s

	if s.isnumeric():
		return int(s)

	if len(s) == 0:
		return 0

	s = s.lower()
	if s[0] == 't':
		return 1
	if s[0] == 'c':
		return 2
	if s[0] == 'm':
		return 3
	return 0

parser.add_argument('--osubase', '-b', help='osu! directory')
parser.add_argument('--mode', '-m', help='Gamemode (ID or name)', nargs='?', default=0, type=parseMode)
parser.add_argument('--username', '-u', help='osu! username', nargs='?', default='')
parser.add_argument('--online', '-o', help='Whether to fetch online scores, normally only local replays will be used', nargs='?', default=False, type=bool)
parser.add_argument('--apikey', '-k', help='osu!api key (Used for fetching scores without a local replay or beatmap)', nargs='?', default='')
parser.add_argument('--mapsfile', '-f', help='The file used for storing online beatmaps list', nargs='?', default='')
parser.add_argument('--scoresfile', '-s', help="The file used for storing user's score list", nargs='?', default='')

if len(sys.argv) == 1:
	try:
		with open('data/secret.json') as f:
			d = json.loads(f.read())
			apiKey = d['apikey']
			osuBase = d['osubase']
			username = d['username']
			mode = parseMode(d['mode'])
			online = True
			bmListFile = d['onlineBeatmapCache'] #'tmp_beatmapList.json'
			scoresFile = d['onlineScoreCache'] #'tmp_scores.json'
	except:
		parser.print_help()
		sys.exit(0)
else:
	args = parser.parseArgs()
	apiKey = args.apikey
	osuBase = args.osubase
	username = args.username
	online = args.online
	if username == '':
		username = OsuDb(f'{osuBase}/osu!.db').username # horribly inefficient but im lazy
	mode = args.mode
	bmListFile = args.mapsfile
	if bmListFile == '':
		def modeToStr(m):
			r = {0:'std', 1:'taiko', 2:'ctb', 3:'mania'}
			return r[m]
		bmListFile = f'tmp_beatmapList_{modeToStr(mode)}.json'
	scoresFile = args.scoresfile
	if scoresFile == '':
		scoresFile = f'tmp_scores_{username}.json'

api = Api(apiKey)

def cacheOnlineBeatmaps(fn):
	bms = api.getBeatmaps(since=datetime(2007, 1, 1), mode=mode)
	with open(fn, 'w') as f:
		f.write(json.dumps(bms))

def cacheOnlineScores(bmFn, fn):
	with open(bmFn) as f:
		bms = json.loads(f.read())
	f = open(fn, 'w')
	print('{', file=f)
	writeComma = False
	for bm in tqdm.tqdm(bms):
		bmID = bm['beatmap_id']
		scores = api.getScores(beatmap=bmID, mode=mode, user=username)
		if writeComma:
			print(',', file=f)
		writeComma = True
		print('"', bmID, '": ', json.dumps(scores), sep='', end='', file=f, flush=True)
	print('}', file=f)
	f.close()

combosByHash = {}
hashesByBm = {}

def loadOnlineHashes(fn):
	with open(fn) as f:
		bms = json.loads(f.read())
	for bm in bms:
		hashesByBm[int(bm['beatmap_id'])] = bm['file_md5']

def loadLocalHashes():
	db = OsuDb(f'{osuBase}/osu!.db')
	for bm in db.beatmaps:
		if bm.mode == mode:
			combosByHash[bm.md5] = bm.circles
			if bm.mapId != 0:
				hashesByBm[bm.mapId] = bm.md5

scoresByMapAndMods = {}

def loadOnlineScores(fn):
	with open(fn) as f:
		scores = json.loads(f.read())
	for bmID,modScores in scores.items():
		if len(modScores) == 0:
			continue

		if not int(bmID) in hashesByBm.keys():
			print(f'Warning: unknown hash for https://osu.ppy.sh/b/{bmID}')
			continue

		h = hashesByBm[int(bmID)]
		for score in modScores:
			scoresByMapAndMods[f'{h}|{score["enabled_mods"]}'] = (int(score['score']), accuracy(mode, *map(int, [score['countmiss'], score['count50'], score['count100'], score['count300'], score['countgeki'], score['countkatu']])))
			combosByHash[h] = totalHits(mode, *map(int, [score['countmiss'], score['count50'], score['count100'], score['count300'], score['countgeki'], score['countkatu']]))

def loadLocalScores():
	replays = [f'{osuBase}/Data/r/{f}' for f in os.listdir(f'{osuBase}/Data/r') if f.endswith('.osr')]

	scores = {}
	for f in replays:
		r = Replay(f, ignoreReplayData=True)
		if r.mode != mode or not r.mapHash in combosByHash.keys() or totalHits(r.mode, r.cntMiss, r.cnt50, r.cnt100, r.cnt300, r.cntGeki, r.cntKatu) < combosByHash[r.mapHash] or r.username != username or r.mode != mode:
			continue

		k = f'{r.mapHash}|{r.mods}'
		if not k in scoresByMapAndMods.keys() or scoresByMapAndMods[k][0] < r.score:
			scoresByMapAndMods[k] = (r.score, accuracy(r.mode, r.cntMiss, r.cnt50, r.cnt100, r.cnt300, r.cntGeki, r.cntKatu))


try:
	loadOnlineHashes(bmListFile)
except:
	if online:
		print('Caching beatmaps... This might take a while')
		cacheOnlineBeatmaps(bmListFile)
		try:
			loadOnlineHashes(bmListFile)
		except:
			print('Something went wrong! Please disable online mode and try again.')
			sys.exit()

loadLocalHashes()

try:
	loadOnlineScores(scoresFile)
except:
	if online:
		print('Caching scores... This might take a really, really long while')
		cacheOnlineScores(scoresFile)
		try:
			loadOnlineScores(scoresFile)
		except:
			print('Something went wrong! Please disable online mode and try again.')
			sys.exit()

loadLocalScores()

collectionsToAdd = {}

def betterScoreExists(m, h, acc):
	allKeys = [k for k in scoresByMapAndMods.keys() if k.startswith(h)]

	def accGroup(acc):
		i = 0
		for n in [82,87,92,95,97,99,100.001]:
			if acc < n:
				return i
			i += 1

	acc0 = accGroup(acc)
	accDiff0 = (0 if m & MOD_EZ else (2 if m & MOD_HR else 1))
	spdDiff0 = (0 if m & MOD_HT else (2 if m & MOD_DT else 1))
	visDiff0 = (2 if (m & MOD_HD) and (m & MOD_FL) else (1 if m & MOD_FL else (1 if m & MOD_HD else 0)))

	def isStrictlyBetterScore(k):
		score, acc = scoresByMapAndMods[k]
		m = int(k.split('|')[1])
		if m & MOD_NF or m & MODS_AUTO:
			return False
		acc1 = accGroup(acc)
		accDiff1 = (0 if m & MOD_EZ else (2 if m & MOD_HR else 1))
		spdDiff1 = (0 if m & MOD_HT else (2 if m & MOD_DT else 1))
		visDiff1 = (2 if (m & MOD_HD) and (m & MOD_FL) else (1 if m & MOD_FL else (1 if m & MOD_HD else 0)))
		if acc1 < acc0 or accDiff1 < accDiff0 or spdDiff1 < spdDiff0 or visDiff1 < visDiff0:
			return False
		if acc1 == acc0 and accDiff1 == accDiff0 and spdDiff1 == spdDiff0 and visDiff1 == visDiff0:
			return False
		return True

	for k in allKeys:
		if isStrictlyBetterScore(k):
			return True
	return False

for k,v in scoresByMapAndMods.items():
	h, m = k.split('|')
	m = int(m)
	score, acc = v
	if m & MOD_NF or m & MODS_AUTO or betterScoreExists(m, h, acc):
		continue # dont count NF scores (cuz they are usually shit) or autopilot/relax/etc scores

	modsStr = ''

	#collections are sorted by name, so show most significant (in terms of acc) mods first, visual mods later

	if m & MOD_DT:
		modsStr += 'DT'
	elif m & MOD_HT:
		modsStr += 'HT'

	if m & MOD_EZ:
		modsStr += 'EZ'
	elif m  & MOD_HR:
		modsStr += 'HR'

	if m & MOD_HD:
		modsStr += 'HD'

	if m & MOD_FL:
		modsStr += 'FL'

	if modsStr == '':
		modsStr = 'NM'

	accStr = ''

	if acc < 82:
		accStr = '00-81'
	elif acc < 87:
		accStr = '82-86'
	elif acc < 92:
		accStr = '87-91'
	elif acc < 95:
		accStr = '92-94'
	elif acc < 97:
		accStr = '95-96'
	elif acc < 99:
		accStr = '97-98'
	else:
		accStr = '99-100'

	collName = f'{modsStr} {accStr}%'
	collectionsToAdd[collName] = collectionsToAdd.get(collName, [])
	collectionsToAdd[collName].append(h)

toDelete = []

db = CollectionDb(f'{osuBase}/collection.db')
for i in range(len(db.collections)):
	coll = db.collections[i]
	n = coll.name.split()
	if len(n) == 2 and n[0].isupper() and n[1].endswith('%') and len(n[1][:-1].split('-')) == 2 and [a.isnumeric() for a in n[1][:-1].split('-')]:
		toDelete.append(i)

for i in toDelete[::-1]:
	del db.collections[i]

for k,v in collectionsToAdd.items():
	db.collections.append(Collection(name=k, hashes=v))

db.save()
print('Done!')