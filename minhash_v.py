#!/usr/bin/python3
# -*- coding: utf-8 -*-
# minhash_v.py

from __future__ import division
from binascii import crc32
from tqdm import tqdm
import ctypes
import group
import multiprocessing as mp
import numba as nb
import numpy as np
import os
import random
import re
import sys

MAXHASH = 2**32-1
C = 4294967311
NF = 100
t = 0.7

@nb.njit(fastmath=True)
def signature_jit(shingles, coeffs):
    return [np.min((coeffs[0][j]*np.array(list(shingles)) + coeffs[1][j])%C) for j in range(NF)]

def shingle(i, aux_data):

    signatures, files, coeffs = aux_data

    with open(files[i],'r',errors='ignore') as fh:
        w = re.split("\W+|_",fh.read().lower())

    shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in range(len(w)-2)}

    # build signatures
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

def hashcount_wrapper(var_data):
    signatures, _, _ = aux_data
    indexes = set(hashcount_jit(var_data,signatures))
    if len(indexes) > 0:
        indexes.add(var_data)
        return indexes

def shingle_wrapper(var_data):
    return shingle(var_data, aux_data)

if __name__ == '__main__':

    coeffs = np.array([[random.randint(0,MAXHASH) for j in range(NF)] for i in range(2)])

    files = [f for f in os.listdir('.') if f.endswith(".txt")]

    if len(sys.argv) > 1:
        files = files[:int(sys.argv[1])]
        
    filenum = len(files)

    signatures = np.ctypeslib.as_array(mp.RawArray(ctypes.c_ulong, filenum*NF)).reshape(filenum,NF)

    aux_data = (signatures, files, coeffs)

    with mp.Pool(mp.cpu_count(), initializer, (aux_data,)) as p:

        # shingle files and create signatures
        for i in tqdm(p.imap(shingle_wrapper,range(filenum),chunksize=100), total=filenum,
            desc="shingling"):
            pass

        # compare signatures
        results = []
        for s in tqdm(p.imap_unordered(hashcount_wrapper,range(1,filenum),chunksize=100),
            total=filenum-1, desc="comparing"):
            if s is not None:
                results_updated = False
                for r in results:
                    if len(r.intersection(s)) > 0:
                        r.update(s)
                        results_updated = True
                        break
                if results_updated is False:
                    results.append(s)

    results = group.group(results)

    # print results
    count = 0
    for s in results:
        count += len(s)
        for index in s:
            print(files[index],end=' ')
        print("")
    print("%d files in %d groups" %(count,len(results)))

