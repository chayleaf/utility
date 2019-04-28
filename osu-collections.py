#!/usr/bin/python3

from osu import collections, osudb

hashCache = {}

dbOsu = osudb.OsuDb('/home/pavlukivan/Games/osu/bancho/osu!.db')

for bm in dbOsu.beatmaps:
	hashCache[bm.md5] = bm

db = collections.CollectionDb('/home/pavlukivan/Games/osu/bancho/collection.db')
for coll in db.collections:
	print('listing', coll.name)
	for h in coll.hashes:
		print(hashCache[h])