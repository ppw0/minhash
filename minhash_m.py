#!/usr/bin/python3
# -*- coding: utf-8 -*-
# minhash_m.py

from binascii import crc32
from tqdm import tqdm
import ctypes
import group
import multiprocessing as mp
import os
import random
import re
import sys

MAXHASH = 2**32-1
C = 4294967311
NF = 100
t = 0.7

def processfile(i):
    with open(files[i],'r',errors='ignore') as fh:
        w = re.split("\W+|_",fh.read().lower())

    shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in range(len(w)-2)}

    # build signatures
    for j in range(NF):
        minhash = C + 1
        for shingle in shingles:
            hashcode = (coeffs[0][j]*shingle + coeffs[1][j]) % C
            if hashcode < minhash:
                minhash = hashcode
        signatures[i*NF+j] = minhash

# similarity function
def hashcount(i):
    return [(files[i],files[j]) for j in range(i-1, -1, -1) if sum(signatures[i*NF+k] == signatures[j*NF+k] for k in range(NF)) > t*NF]

if __name__ == '__main__':
    coeffs = [[random.randint(0,MAXHASH) for j in range(NF)] for i in range(2)]
    
    files = [os.path.join(root,f) for root,_,fnames in os.walk('.') for f in fnames]
    if len(sys.argv) > 1:
        files = files[:int(sys.argv[1])]
    filenum = len(files)

    # shared array
    signatures = mp.RawArray(ctypes.c_ulong, filenum*NF)
    
    # initialize pool
    with mp.Pool(mp.cpu_count()) as p:
        for i in tqdm(p.imap(processfile,range(filenum),chunksize=100),total=filenum,desc="shingling"):
            pass
        results = [r for l in tqdm(p.imap_unordered(hashcount,range(1,filenum),chunksize=100),total=filenum-1,desc="comparing") for r in l]

    group.print_complete(results)
