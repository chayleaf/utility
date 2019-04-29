from osu import *
import argparse, sys, json, os

parser = argparse.ArgumentParser(description='Refresh, backup scores.db and remove duplicates')
parser.add_argument('--osubase', '-b', help='osu! directory')
parser.add_argument('--backup', '-d', help='Backup filename (backup is restored and applied at the same time)', nargs='?', default='')

if len(sys.argv) == 1:
	try:
		with open('data/secret.json') as f:
			d = json.loads(f.read())
			osuBase = d['osubase']
			backup = d['scoresBackup']
	except:
		parser.print_help()
		sys.exit(0)
else:
	args = parser.parseArgs()
	osuBase = args.osubase
	backup = args.backup

scores = ScoresDb(f'{osuBase}/scores.db')

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

replays = [f'{osuBase}/Data/r/{f}' for f in os.listdir(f'{osuBase}/Data/r') if f.endswith('.osr')]

for f in replays:
	r = Replay(f, ignoreReplayData=True)
	# TODO check combo

	k = r.mapHash

	if not k in newScoresByHash.keys():
		newScoresByHash[k] = []
	newScoresByHash[k].append(r)

def replayKey(r):
	return r.score

for k in newScoresByHash.keys():
	usedHashes = set()
	a = [*sorted([*newScoresByHash[k]], reverse=True)]
	newScoresByHash[k] = []
	for r in a:
		if r.replayHash in usedHashes:
			continue
		usedHashes.add(r.replayHash)
		newScoresByHash[k].append(r)

scores.scoresByHash = newScoresByHash
scores.save(f'{osuBase}/scores.db')
scores.save(backup)