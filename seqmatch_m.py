#!/usr/bin/python3
# -*- coding: utf-8 -*-
# seqmatch_m.py

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
            print ("access lock at "+str(f1)+" and "+str(f2))
            continue
        break
    return (r,f1,f2)

if __name__ == '__main__':

    files = [os.path.join(root,f) for root,_,filenames in os.walk('.') for f in filenames]
    pairs = itertools.combinations(files,2)
    
    with mp.Pool(mp.cpu_count()) as p:
        results = [[f1,f2] for r,f1,f2 in p.imap_unordered(smratio,pairs) if r > 80]
    
    group.print_complete(results)
