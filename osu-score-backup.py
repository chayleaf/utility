#!/usr/bin/python3
from osu import *
import argparse, sys, json, os, shutil

parser = argparse.ArgumentParser(description='Refresh, backup scores.db, remove duplicates and possibly backup replays')
parser.add_argument('--osubase', '-b', help='osu! directory')
parser.add_argument('--scorebackup', '-s', help='Score db backup filename (backup is restored and applied at the same time)', nargs='?', default='')
parser.add_argument('--replaybackup', '-r', help='Replays backup directory (they are applied to the score db, and local game replays are copied there)', nargs='?', default='')

if len(sys.argv) == 1:
	try:
		with open('data/secret.json') as f:
			d = json.loads(f.read())
			osuBase = d['osubase']
			backup = d['scoresBackup']
			rBak = d['replaysDir']
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
		if r.replayHash in usedHashes:
			continue
		usedHashes.add(r.replayHash)
		newScoresByHash[k].append(r)

scores.scoresByHash = newScoresByHash
scores.save(f'{osuBase}/scores.db')
scores.save(backup)