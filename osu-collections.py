#!/usr/bin/python3
from datetime import datetime
from osu import *
import json, tqdm, os, sys, argparse, shutil

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
parser.add_argument('--online', '-o', help='Fetch online scores, normally only local replays will be used', action='store_true')
parser.add_argument('--apikey', '-k', help='osu!api key (Used for fetching scores without a local replay or beatmap)', nargs='?', default='')
parser.add_argument('--mapsfile', '-f', help='The file used for storing online beatmaps list', nargs='?', default='')
parser.add_argument('--scoresfile', '-s', help="The file used for storing user's score list", nargs='?', default='')
parser.add_argument('--replaysdir', '-r', help="The directory used for storing and backupping replay files (warning: they will be renamed upon load)", nargs='?', default='')

if len(sys.argv) == 1:
	try:
		with open('data/secret.json') as f:
			d = json.loads(f.read())
			apiKey = d['apikey']
			osuBase = d['osubase']
			username = d['username']
			mode = parseMode(d['mode'])
			online = True
			bmListFile = d['onlineBeatmapCache']
			scoresFile = d['onlineScoreCache']
			replaysDir = d['replaysDir']
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
		username = OsuDb(os.path.join(osuBase, 'osu!.db')).username # horribly inefficient but idc
	mode = args.mode
	bmListFile = args.mapsfile
	if bmListFile == '':
		def modeToStr(m):
			r = {0:'std', 1:'taiko', 2:'ctb', 3:'mania'}
			return r[m]
		bmListFile = os.path.join('data', f'beatmapList_{modeToStr(mode)}.json')
	scoresFile = args.scoresfile
	if scoresFile == '':
		scoresFile = os.path.join('data', 'scores_{username}.json')
	replaysDir = args.replaysdir

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
odByHash = {}

def loadOnlineHashes(fn):
	with open(fn) as f:
		bms = json.loads(f.read())
	for bm in bms:
		hashesByBm[int(bm['beatmap_id'])] = bm['file_md5']
		if bm['max_combo'] is not None:
			combosByHash[bm['file_md5']] = int(bm['max_combo'])

def loadLocalHashes():
	db = OsuDb(os.path.join(osuBase, 'osu!.db'))
	for bm in db.beatmaps:
		if bm.mode == mode:
			if mode == MODE_TAIKO:
				combosByHash[bm.md5] = bm.circles
			if bm.mapId != 0:
				hashesByBm[bm.mapId] = bm.md5
			odByHash[bm.md5] = bm.OD

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

def loadReplays(base=None): #also backup
	customDir = True
	if base is None:
		customDir = False
		base = os.path.join(osuBase, 'Data', 'r')
	replays = [os.path.join(base, f) for f in os.listdir(base) if f.endswith('.osr')]

	scores = {}
	for f in replays:
		r = Replay(f, ignoreReplayData=True)

		if customDir:
			genFn = r.generateFilename()
			if os.path.basename(f) != genFn:
				newPath = os.path.join(osuBase, genFn)
				os.rename(f, newPath)
				r.filename = newPath
		elif replaysDir != '': #processing osu replays dir; backup the replay if backup path specified
			newPath = os.path.join(replaysDir, os.path.basename(f))
			if not os.path.isfile(newPath):
				shutil.copy2(f, newPath)

		if r.mode != mode:
			continue

		if r.perfectCombo: #max combo
			combosByHash[r.mapHash] = r.combo #ideally this should be done for each replay before the other stuff, but who cares amirite

		# If replay user is different; if map is not loaded; if replay isn't complete.
		if r.username != username or r.mapHash not in combosByHash.keys() or totalHits(r.mode, r.cntMiss, r.cnt50, r.cnt100, r.cnt300, r.cntGeki, r.cntKatu) < combosByHash[r.mapHash]:
			continue

		k = f'{r.mapHash}|{r.mods}'
		if not k in scoresByMapAndMods.keys() or scoresByMapAndMods[k][0] < r.score:
			scoresByMapAndMods[k] = (r.score, accuracy(r.mode, r.cntMiss, r.cnt50, r.cnt100, r.cnt300, r.cntGeki, r.cntKatu))

def downloadOnlineReplays(scoresFile):
	# TODO find a decent method to batch download replays

	with open(scoresFile) as f:
		scores = json.loads(f.read())
	
	for modScores in tqdm.tqdm(scores):
		for s in modScores:
			if s['replay_available'] == 1:
				pass

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
		# TODO
		#yn = input('Also download every available replay? (y/n): ')
		#if yn[0] in 'yY':
		#	print('Caching replay... This might take... some time')
		#	downloadOnlineReplays(scoresFile)

		try:
			loadOnlineScores(scoresFile)
		except:
			print('Something went wrong! Please disable online mode and try again.')
			sys.exit()

loadReplays(replaysDir)
loadReplays()

collectionsToAdd = {}

accRanges = [82,87,92,95,97,99,101]

def betterScoreExists(m, h, acc):
	allKeys = [k for k in scoresByMapAndMods.keys() if k.startswith(h)]

	def accGroup(acc):
		i = 0
		for n in accRanges:
			if acc < n:
				return i
			i += 1

	def hitWindow(h, m):
		if h in odByHash.keys():
			OD = odByHash[h]
		else:
			OD = 5

		if m & MOD_EZ:
			OD *= 0.5

		if m & MOD_HR:
			OD = min(10, OD * 1.4)

		if OD > 5:
			hw = 70 + (40 - 70) * (OD - 5) / 5
		elif OD < 5:
			hw = 70 - (70 - 100) * (5 - OD) / 5
		else:
			hw = 70

		if m & MOD_DT:
			hw /= 1.5

		return hw


	acc0 = accGroup(acc)
	#accDiff0 = (0 if m & MOD_EZ else (2 if m & MOD_HR else 1))
	hit300_0 = hitWindow(h, m)
	spdDiff0 = (0 if m & MOD_HT else (2 if m & MOD_DT else 1))
	visDiff0 = (2 if (m & MOD_HD) and (m & MOD_FL) else (1 if m & MOD_FL else (1 if m & MOD_HD else 0)))

	def isStrictlyBetterScore(k):
		score, acc = scoresByMapAndMods[k]
		h,m = k.split('|')
		m = int(m)
		if m & MOD_NF or m & MODS_AUTO:
			return False
		acc1 = accGroup(acc)
		#accDiff1 = (0 if m & MOD_EZ else (2 if m & MOD_HR else 1))
		hit300_1 = hitWindow(h, m)
		spdDiff1 = (0 if m & MOD_HT else (2 if m & MOD_DT else 1))
		visDiff1 = (2 if (m & MOD_HD) and (m & MOD_FL) else (1 if m & MOD_FL else (1 if m & MOD_HD else 0)))
		if acc1 < acc0 or hit300_1 > hit300_0 or spdDiff1 < spdDiff0 or visDiff1 < visDiff0:
			return False
		if acc1 == acc0 and hit300_1 == hit300_0 and spdDiff1 == spdDiff0 and visDiff1 == visDiff0:
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

	oldN = '00'
	for n in accRanges:
		if acc < n:
			accStr = f'{oldN}-{n-1}%'
			break
		oldN = n

	collName = f'{modsStr} {accStr}'
	collectionsToAdd[collName] = collectionsToAdd.get(collName, [])
	collectionsToAdd[collName].append(h)

toDelete = []

db = CollectionDb(os.path.join(osuBase, 'collection.db'))
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