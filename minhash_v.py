#!/usr/bin/python
# -*- coding: utf-8 -*-
# minhash_v.py: vectorized version of minhash_m.py, with Numba JIT compiler decoration. the use
# of an initializer is mandatory - besides the several orders-of-magnitude speedup, it avoids the
# synchronization stalls with large inputs and a memory bubble (probably caused by serialization).
# not compatible with Windows (the changes written to the numpy array do not get carried back to
# the main process.)

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
t = 0.9 # similarity threshold

@nb.njit(fastmath=True)
def signature_jit(shingles, coeffs):
    return [np.min((coeffs[0][j]*np.array(list(shingles)) + coeffs[1][j])%C) for j in range(NF)]

def shingle(i, aux_data):

    signatures, files, coeffs = aux_data

    with open(files[i],'r',errors='ignore') as fh:
        w = re.split("\W+|_",fh.read().lower()) # words

    # files with less than three words or terms are treated as duplicates
    shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in range(len(w)-2)}
  
    # build signature vectors
    if len(shingles) == 0:
        signatures[i] = C + 1
    else:
        signatures[i] = signature_jit(shingles, coeffs)
    
@nb.njit(fastmath=True)
def hashcount_jit(i, signatures):
    sig_i = signatures[i]
    return [j for j in range(i-1, -1, -1) if np.sum(sig_i == signatures[j]) > t*NF]

aux_data = None
            
def initializer(init_data):
    global aux_data
    aux_data = init_data    
    
def hashcount(i):
    signatures, _, _ = aux_data
    indexes = set(hashcount_jit(i,signatures))
    if len(indexes) > 0:
        indexes.add(i)
        return indexes
        
def shingle_wrapper(var_data):
    return shingle(var_data, aux_data)

if __name__ == '__main__':
    
    # random hash function: h(x) = (a*x + b) % c
    # x - input value, coefs - random coefficients
    # coeffs can contain duplicates, but the probability of that is very small
    coeffs = np.array([[random.randint(0,MAXHASH) for j in range(NF)] for i in range(2)])
    
    # get list of files    
    files = [f for f in os.listdir('.') if f.endswith(".txt")]
    
    if len(sys.argv) > 1:
        filenum = int(sys.argv[1])
        files = files[:filenum]
    else:
        filenum = len(files)

    # shared array
    signatures = np.ctypeslib.as_array(mp.RawArray(ctypes.c_ulong, filenum*NF)).reshape(filenum,NF)
    
    # initialize pool
    aux_data = (signatures, files, coeffs)
    
    with mp.Pool(mp.cpu_count(), initializer, (aux_data,)) as p:
    
        # shingle the files and create signatures
        for i in tqdm(p.imap(shingle_wrapper,range(filenum),chunksize=100), total=filenum, 
            desc="shingling"):
            pass
        
        # compare signatures
        results = []
        for s in tqdm(p.imap_unordered(hashcount,range(1,filenum),chunksize=100), total=filenum-1,
            desc="comparing"):
            if s is not None:
                results_updated = False
                for r in results:
                    if len(r.intersection(s)) > 0:
                        r.update(s)
                        results_updated = True
                        break
                if results_updated is False:
                    results.append(s)
    
    # group results
    import group
    results = group.group(results)
    
    # print results
    count = 0
    for s in results:
        count += len(s)
        for index in s:
            print(files[index],end=' ')
        print("")
    print("%d files in %d groups" %(count,len(results)))
    
