#!/usr/bin/python3
# -*- coding: utf-8 -*-
# minhash.py

from binascii import crc32
from tqdm import tqdm # pretty progress bars
import group
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
    files = [os.path.join(root,f) for root,_,fnames in os.walk('.') for f in fnames]
    if len(sys.argv) > 1:
        files = files[:int(sys.argv[1])]
    filenum = len(files)

    # random hash function: h(x) = (a*x + b) % C
    # x - input value; a,b - random coefficients
    coeffs = [[random.randint(0, MAXHASH) for j in range(NF)] for i in range(2)]

    sig = {} # documents represented as signature vectors
    results = []

    for i in tqdm(range(filenum)):

        # shingling
        with open(files[i],'r',errors='ignore') as fh:
            w = re.split("\W+|_", fh.read().lower()) # words

        # files with less than three words or terms are treated as dupes
        shingles = {crc32((w[j]+" "+w[j+1]+" "+w[j+2]).encode()) & 0xffffffff for j in range(len(w)-2)}

        # build signature vectors
        sig_vec = []
        for j in range(NF):
            minhash = C + 1 # maximum possible hash value
            for shingle in shingles:
                hashcode = (coeffs[0][j]*shingle + coeffs[1][j]) % C
                if hashcode < minhash:
                    minhash = hashcode
            sig_vec.append(minhash)
        sig[files[i]] = sig_vec

        # compare signatures
        for j in range(i-1, -1, -1):
            if sum(sig_vec[k] == sig[files[j]][k] for k in range(NF)) > t*NF:
                results.append((files[i],files[j]))
    
    group.print_complete(results)
