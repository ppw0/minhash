#!/usr/bin/python3
# -*- coding: utf-8 -*-
# seqmatch.py

from difflib import SequenceMatcher as sm
import group
import itertools
import os

def smratio(f1,f2):
    return int(100*sm(None, open(f1).read(), open(f2).read()).ratio())
    # alternatively use .quick_ratio() or .real_quick_ratio()

if __name__ == '__main__':

    # get folder contents and generate unordered pairs of files
    files = [os.path.join(root,f) for root,_,filenames in os.walk('.') for f in filenames]
    pairs = itertools.combinations(files,2)
    
    # build list of similar files
    results = [[f1,f2] for f1,f2 in pairs if smratio(f1,f2) > 80]
    
    group.print_complete(results)
