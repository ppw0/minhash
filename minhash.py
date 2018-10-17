#!/usr/bin/python
# -*- coding: utf-8 -*-
# minhash.py: return all similar text files quickly. based on MinHash and Jaccard similarity
# estimation algorithms. useful only for small document sizes (n < 5000). special thanks to Chris
# McCormick: http://mccormickml.com/2015/06/12/minhash-tutorial-with-python-code/

from __future__ import division
from binascii import crc32
from tqdm import tqdm # pretty progress bars
import os
import random
import re
import sys

MAXHASH = 2**32-1 # the maximum hash number a shingle can have
C = 4294967311 # next prime number larger than MAXHASH
NF = 100 # number of random hash functions to be generated
t = 0.7 # similarity threshold

if __name__ == '__main__':

    # get list of files
    if len(sys.argv) > 1:
        filenum = int(sys.argv[1])
        files = os.listdir('.')[:filenum]
    else:
        files = os.listdir('.')
        filenum = len(files)

    # random hash function: h(x) = (a*x + b) % c
    # x - input value, coefs - random coefficients
    # coefs can contain duplicates, but the probability of that is very small
    coefs = [[random.randint(0, MAXHASH) for j in range(NF)] for i in range(2)]

    sig = {} # documents represented as signature vectors
    results = []

    for i in tqdm(range(filenum)):

        # shingling
        with open(files[i],'r',errors='ignore') as fh:
            w = re.split("\W+|_", fh.read().lower()) # words

        # the following loop hashes shingles from word triplets, but can leave empty shingle
        # sets, so files with less than three words or terms are treated as duplicates.
        shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in 
            range(len(w)-2)}

        # building signature vectors
        sig_vec = []

        for j in range(NF):
            minhash = C + 1 # max possible hash value
            for shingle in shingles:
                hashcode = (coefs[0][j]*shingle + coefs[1][j]) % C
                if hashcode < minhash:
                    minhash = hashcode
            sig_vec.append(minhash)
        
        sig[files[i]] = sig_vec

        # compare signatures
        for j in range(i-1, -1, -1):
            if sum(sig_vec[k] == sig[files[j]][k] for k in range(NF)) > t*NF:
                results.append((files[i],files[j]))
    
    # group results
    import group
    group.print_dupes(group.group(results))
