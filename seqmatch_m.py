#!/usr/bin/python
# -*- coding: utf-8 -*-
# seqmatch_m.py: multithreaded version of seqmatch.py.

# similarity function based on SequenceMatcher
from difflib import SequenceMatcher as sm
import group
import itertools
import multiprocessing as mp
import os

def smratio(pair):
	f1,f2 = pair
	while True:
		try:
			r = int(100*sm(None, open(f1).read(), open(f2).read()).ratio())
		except OSError:
			#print ("access lock at "+str(f1)+" and "+str(f2))
			continue
		break
	return (r,f1,f2)

if __name__ == '__main__':

    # get folder contents and generate all unordered pairs of files
	pairs = itertools.combinations(os.listdir(os.getcwd()),2)
	
    with mp.Pool(mp.cpu_count()) as p:
	
        similar = [[f1,f2] for r,f1,f2 in p.imap_unordered(smratio,pairs) if r > 80]
	
	group.print_dupes(group.group(similar))
