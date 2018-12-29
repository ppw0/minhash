#!/usr/bin/python
# -*- coding: utf-8 -*-
# minhash_dss.py

from __future__ import division
from binascii import crc32
from tqdm import tqdm # pretty progress bars
import ctypes
import group
import multiprocessing as mp
import os
import random
import re
import sys

MAXHASH = 2**32-1 # the maximum hash number a shingle can have
C = 4294967311 # next prime number larger than MAXHASH
NF = 100 # number of random hash functions to be generated
t = 0.7 # similarity threshold
N = 0.3 # size threshold

def processfile(i):
    with open(files[i][0],'r',errors='ignore') as fh:
        w = re.split("\W+|_",fh.read().lower()) # words

    # the following loop hashes shingles from word triplets, but can leave empty shingle
    # sets, so files with less than three words or terms are treated as duplicates.
    shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in range(len(w)-2)}

    # building signature vectors
    for j in range(NF):
        minhash = C + 1
        for shingle in shingles:
            hashcode = (coefs[0][j]*shingle + coefs[1][j]) % C
            if hashcode < minhash:
                minhash = hashcode
        signatures[i*NF+j] = minhash
    
def hashcount(i): # similarity function based on counting hashes
    l = []
    for j in range(i-1, -1, -1):
        if files[j][1] > files[i][1]*(1+N):
            break
        if sum(signatures[i*NF+k] == signatures[j*NF+k] for k in range(NF)) > t*NF:
            l.append((files[i][0],files[j][0]))
    return l

if __name__ == '__main__':
    
    # random hash function: h(x) = (a*x + b) % c
    # x - input value, coefs - random coefficients
    # coefs can contain duplicates, but the probability of that is very small
    coefs = [[random.randint(0,MAXHASH) for j in range(NF)] for i in range(2)]
    
    # get list of files and their sizes, sort it by size
    files = [(f,os.path.getsize(f)) for f in os.listdir('.')]
    files.sort(key = lambda x: x[1], reverse = True)
    
    if len(sys.argv) > 1:
        files = files[:int(sys.argv[1])]
        
    filenum = len(files)

    # shared array
    signatures = mp.RawArray(ctypes.c_ulong, filenum*NF)
    
    # initialize pool
    with mp.Pool(mp.cpu_count()) as p:
    
        for i in tqdm(p.imap(processfile,range(filenum)),total=filenum):
            pass
    
        results = [r for l in tqdm(p.imap_unordered(hashcount,range(1,filenum),chunksize=100),
            total=filenum-1) for r in l]

    # group results
    group.print_dupes(group.group(results))
