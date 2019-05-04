#!/usr/bin/python3
from osu import *
import argparse, sys, json, os, shutil, datetime

parser = argparse.ArgumentParser(description='Refresh, backup scores.db, remove duplicates and possibly backup replays')
parser.add_argument('--osubase', '-b', help='osu! directory')
parser.add_argument('--scorebackup', '-s', help='Score db backup filename (backup is restored and applied at the same time)', nargs='?', default='')
parser.add_argument('--replaybackup', '-r', help='Replays backup directory (they are applied to the score db, and local game replays are copied there)', nargs='?', default='')

scoresByMapAndMode = {}
lastPlayDateByMap = {}
mapInfoByHash = {}

if len(sys.argv) == 1:
	try:
		with open('data/secret.json') as f:
			d = json.loads(f.read())
			osuBase = d['osubase']
			backup = d['scoresBackup']
			rBak = d['replaysDir']
			scoresFile = d['onlineScoreCache']
			bmListFile = d['onlineBeatmapCache']
			# TODO cli
			mode = 1

			hashesByBm = {}
			with open(bmListFile) as f:
				bms = json.loads(f.read())

			for bm in bms:
				approvedConvert = {-2:2,-1:2,0:2,1:4,2:5,3:6,4:7}
				mapInfoByHash[bm['file_md5']] = (int(bm['beatmap_id']), int(bm['beatmapset_id']), approvedConvert[int(bm['approved'])])
				hashesByBm[int(bm['beatmap_id'])] = bm['file_md5']

			with open(scoresFile) as f:
				scores = json.loads(f.read())

			for bmID,modScores in scores.items():
				if len(modScores) == 0:
					continue

				if not int(bmID) in hashesByBm.keys():
					print(f'Warning: unknown hash for https://osu.ppy.sh/b/{bmID}')
					continue

				h = hashesByBm[int(bmID)]
				for score in modScores:
					k = f'{h}|{mode}'
					t = datetime.datetime.fromisoformat(score['date'])
					s = int(score['score'])

					if not k in scoresByMapAndMode.keys() or scoresByMapAndMode[k][0] < s:
						r = rank(mode, *map(int, [score['countmiss'], score['count50'], score['count100'], score['count300'], score['countgeki'], score['countkatu']]), mods=Mods(score['enabled_mods']))
						scoresByMapAndMode[k] = (s, r)

					if not h in lastPlayDateByMap.keys() or lastPlayDateByMap[h] < t:
						lastPlayDateByMap[h] = t
	except:
		parser.print_help()
		sys.exit(0)
else:
	args = parser.parseArgs()
	osuBase = args.osubase
	backup = args.scorebackup
	rBak = args.replaybackup

scores = ScoresDb(os.path.join(osuBase, 'scores.db'))

newScoresByHash = scores.scoresByHash
if backup != '':
	try:
		scores2 = ScoresDb(backup)
		for k,v in scores2.scoresByHash.items():
			if not k in newScoresByHash.keys():
				newScoresByHash[k] = []
			newScoresByHash[k].extend(v)
	except:
		pass

gameReplayDir = os.path.join(osuBase, 'Data', 'r')

if rBak != '':
	replays = [os.path.join(rBak, f) for f in os.listdir(rBak) if f.endswith('.osr')]
	for f in replays:
		r = Replay(f, ignoreReplayData=True)
		genFn = r.generateFilename()
		if os.path.basename(f) != genFn:
			newPath = os.path.join(rBak, genFn)
			os.rename(f, newPath)
			r.filename = newPath
			f = newPath
		newPath = os.path.join(gameReplayDir, os.path.basename(f))
		if not os.path.isfile(newPath):
			shutil.copy2(f, newPath)

replays = [os.path.join(gameReplayDir, f) for f in os.listdir(gameReplayDir) if f.endswith('.osr')]

for f in replays:
	r = Replay(f, ignoreReplayData=True)

	k = r.mapHash

	if not k in newScoresByHash.keys():
		newScoresByHash[k] = []
	newScoresByHash[k].append(r)

	if rBak != '':
		newPath = os.path.join(rBak, os.path.basename(f))
		if not os.path.isfile(newPath):
			shutil.copy2(f, newPath)

def replayKey(r):
	return r.score

keys = [*newScoresByHash.keys()]
for k in keys:
	usedHashes = set()
	a = newScoresByHash[k]
	a.sort(key=replayKey, reverse=True)
	newScoresByHash[k] = []
	for r in a:
		h = r.mapHash
		k1 = f'{h}|{r.mode}'
		t = r.timestamp
		s = r.score
		if (not k1 in scoresByMapAndMode.keys()) or scoresByMapAndMode[k1][0] < s:
			rnk = rank(r.mode, r.cntMiss, r.cnt50, r.cnt100, r.cnt300, r.cntGeki, r.cntKatu, mods=r.mods)
			scoresByMapAndMode[k1] = (s, rnk)

		if not h in lastPlayDateByMap.keys() or lastPlayDateByMap[h] < t:
			lastPlayDateByMap[h] = t
	for r in a:
		if r.hash in usedHashes:
			continue
		usedHashes.add(r.hash)
		newScoresByHash[k].append(r)

scores.scoresByHash = newScoresByHash
scores.save()
scores.save(backup)

osudb = OsuDb(os.path.join(osuBase, 'osu!.db'))
for bm in osudb.beatmaps:
	lastPlayDateByMap[bm.hash] = max(bm.lastPlayed, lastPlayDateByMap.get(bm.hash, datetime.datetime(1,1,1)))

for bm in osudb.beatmaps:
	bm.lastPlayed = lastPlayDateByMap[bm.hash]

	if bm.mapId == 0 and bm.mapsetId == -1:
		if bm.hash in mapInfoByHash.keys():
			bm.mapId, bm.mapsetId, bm.state = mapInfoByHash[bm.hash]
		else:
			pass #TODO load .osu file, need Beatmap class for that

	for m in range(4):
		displayM = m
		if bm.mode != Mode.STD:
			displayM = bm.mode #if the map isn't a convert, display the rank for the map's mode in any mode
		k = f'{bm.hash}|{displayM}'
		if k in scoresByMapAndMode.keys():
			bm.isNew = False
			bm.playerRank[m] = scoresByMapAndMode[k][1]
osudb.save(os.path.join(osuBase, 'osu!.db'))
print('Done!')