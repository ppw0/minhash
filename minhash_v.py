#!/usr/bin/python
# -*- coding: utf-8 -*-
# minhash_v.py: vectorized version of minhash_m.py, with Numba JIT compiler decoration. the use
# of an initializer is mandatory - besides the several orders-of-magnitude speedup, it avoids the
# synchronization stalls with large inputs.

from __future__ import division
from binascii import crc32
from tqdm import tqdm # pretty progress bars
import ctypes
import multiprocessing as mp
import numba as nb
import numpy as np
import os
import random
import re
import sys

MAXHASH = 2**32-1 # the maximum hash number a shingle can have
C = 4294967311 # next prime number larger than MAXHASH
NF = 100 # number of random hash functions to be generated
t = 0.7 # similarity threshold

@nb.njit(fastmath=True)
def signature(shingles):
    return [np.min((coefs[0][j]*np.array(list(shingles)) + coefs[1][j])%C) for j in range(NF)]

def processfile(i):
    with open(files[i],'r',errors='ignore') as fh:
        w = re.split("\W+|_",fh.read().lower()) # words

    # the following statement hashes shingles from word triplets, but can leave empty shingle
    # sets, so files with less than three words or terms are treated as duplicates.
    shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in range(len(w)-2)}
  
    # build signature vectors
    if len(shingles) == 0:
        signatures[i] = C + 1
    else:
        signatures[i] = signature(shingles)
            
@nb.njit(fastmath=True)
def hashcount(i, aux_data):
    signatures = aux_data
    sig_i = signatures[i]
    return [(i,j) for j in range(i-1, -1, -1) if np.sum(sig_i == signatures[j]) > t*NF]

aux_data = None
            
def initializer(init_data):
    global aux_data
    aux_data = init_data

def hashcount_wrapper(var_data):
    return hashcount(var_data, aux_data)

if __name__ == '__main__':
    
    # random hash function: h(x) = (a*x + b) % c
    # x - input value, coefs - random coefficients
    # coefs can contain duplicates, but the probability of that is very small
    coefs = np.array([[random.randint(0,MAXHASH) for j in range(NF)] for i in range(2)])
    
    # get list of files
    if len(sys.argv) > 1:
        filenum = int(sys.argv[1])
        files = os.listdir('.')[:filenum]
    else:
        files = os.listdir('.')
        filenum = len(files)

    # shared array
    signatures_base = mp.RawArray(ctypes.c_ulong, filenum*NF)
    signatures = np.ctypeslib.as_array(signatures_base).reshape(filenum,NF)
    
    # initialize pool
    aux_data = (signatures)
    
    p = mp.Pool(mp.cpu_count(), initializer, (aux_data,))
    
    for i in tqdm(p.imap(processfile,range(filenum),chunksize=100),total=filenum):
        pass
        
    results = []
    for l in tqdm(p.imap_unordered(hashcount_wrapper,range(1,filenum),chunksize=100),
        total=filenum-1):
        for r in l:
            i,j = r
            results.append((files[i],files[j]))
            
    p.close()
    p.join()
    
    # group results
    import group
    group.print_dupes(group.group(results))
