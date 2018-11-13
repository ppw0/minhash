#!/usr/bin/python
# -*- coding: utf-8 -*-
# minhash_m_init.py: Windows-compatible version of minhash_m.py, with an initializer to preserve
# global variable states. comparable running time to Unix-only version. special thanks to Venkatesh
# Prasad Ranganath: https://medium.com/@rvprasad/data-and-chunk-sizes-matter-when-using-multiproces
# sing-pool-map-in-python-5023c96875ef

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

def processfile(i, aux_data):

    signatures, files, coefs = aux_data
    
    with open(files[i],'r',errors='ignore') as fh:
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
        
def hashcount(i, aux_data): # similarity function based on counting hashes

    signatures, files, _ = aux_data
    
    return [(files[i],files[j]) for j in range(i-1, -1, -1) if sum(signatures[i*NF+k] == 
        signatures[j*NF+k] for k in range(NF)) > t*NF]

aux_data = None
            
def initializer(init_data):
    global aux_data
    aux_data = init_data

def hashcount_wrapper(var_data):
    return hashcount(var_data, aux_data)
    
def processfile_wrapper(var_data):
    return processfile(var_data, aux_data)
    
if __name__ == '__main__':
    
    # random hash function: h(x) = (a*x + b) % c
    # x - input value, coefs - random coefficients
    # coefs can contain duplicates, but the probability of that is very small
    coefs = [[random.randint(0,MAXHASH) for j in range(NF)] for i in range(2)]

    # get list of files
    if len(sys.argv) > 1:
        filenum = int(sys.argv[1])
        files = os.listdir('.')[:filenum]
    else:
        files = os.listdir('.')
        filenum = len(files)

    # shared array
    signatures = mp.RawArray(ctypes.c_ulong, filenum*NF)
    
    # initialize pool
    aux_data = (signatures,files,coefs)
    
    with mp.Pool(mp.cpu_count(), initializer, (aux_data,)) as p:
    
        for i in tqdm(p.imap(processfile_wrapper,range(filenum),chunksize=100),total=filenum):
            pass
        
        results = [r for l in tqdm(p.imap_unordered(hashcount_wrapper,range(1,filenum),
            chunksize=100),total=filenum-1) for r in l]

    # group results
    group.print_dupes(group.group(results))
