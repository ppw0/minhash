#!/usr/bin/python
# -*- coding: utf-8 -*-
# seqmatch.py: returns all similar files, based on matching sequences.

# similarity function based on SequenceMatcher
from difflib import SequenceMatcher as sm
import itertools
import group
import os

def smratio(f1,f2):
	return int(100*sm(None, open(f1).read(), open(f2).read()).ratio())
	#return int(100*sm(None, open(f1).read(), open(f2).read()).quick_ratio())
	#return int(100*sm(None, open(f1).read(), open(f2).read()).real_quick_ratio())

if __name__ == '__main__':

	# get folder contents and generate unordered pairs of files
	pairs = itertools.combinations(os.listdir(os.getcwd()),2)
	
	# build list of similar files
	similar = [[f1,f2] for f1,f2 in pairs if smratio(f1,f2) > 80]
	
	group.print_groups(group.group(similar))
