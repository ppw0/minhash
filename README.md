# minhash
an implementation of the MinHash algorithm in Python.

# a short manifest for each file.

- README.md: this text file.

- group.py: groups related item pairs into lists. converts list of related pairs into lists of related items. helper module.

- seqmatch.py: return all similar text files, based on matching sequences.

- seqmatch_m.py: returns all similar files, multithreaded version of seqmatch.py.

- minhash.py: return all similar text files quickly. based on MinHash and Jaccard similarity estimation algorithms. useful only for small document sizes (n < 5000). special thanks to Chris McCormick: http://mccormickml.com/2015/06/12/minhash-tutorial-with-python-code/

- minhash_m.py: minhash with multiprocessing, shared memory access and simplified data structures for performance reasons. (Unix-like compatible only)

- minhash_m_init.py: Windows-compatible version of minhash_m, with an initializer to preserve global variable states. comparable running time to minhash_m. special thanks to Venkatesh Prasad Ranganath: https://medium.com/@rvprasad/data-and-chunk-sizes-matter-when-using-multiprocessing-pool-map-in-python-5023c96875ef

- minhash_dss.py: minhash_m with a simple neighbor heuristic to delimit search space, significantly reducing running time while still covering a large majority of results.

- minhash_v.py: vectorized version of minhash_m, with Numba JIT compiler decoration. the use of an initializer is mandatory - besides the several orders-of-magnitude speedup, it avoids the synchronization stalls with large inputs.

# lessons learned.
- an introduction of a simple heuristic can significantly decrease running time while still finding a large majority of similar files.
- don't use `map` if the input iterator is very large; it will lead to a segmentation fault. this came up while trying to generate pairs for the `hashcount` function, until that whole approach was discarded and replaced with a much better one.
- with `imap` and `imap_unordered`, if the function returns results faster than they can be consumed, you will experience a memory bubble (example: 620000 signatures take up 6 GB of RAM during comparison phase with imap_unordered and a `for` loop to sort results):
    - https://stackoverflow.com/questions/40922526/memory-usage-steadily-growing-for-multiprocessing-pool-imap-unordered
    - https://stackoverflow.com/questions/9862091/iteration-over-pool-imap-unordered
- pypy3 is significantly faster than python3, but it cannot be used with Numba.
- minimize your inputs before passing them off to a function. (example: grouping results uses `connected_components` from networkx which has near-exponential space complexity)
- when in doubt, vectorize.

# some measurements.
a random selection of non-duplicate text files of varying sizes (0-1767kb). cpu: i7-3770.

|       script      | interpreter | 1500       | 5000     |   10000   |   20000    |    50000   |
| :---------------- | ----------- | :--------- | :------- | :-------- | :--------- | :--------- |
| seqmatch.py       | python3     | `2503.13s` |          |           |            |            |
| seqmatch_m.py     | python3     | `658.70s`  |          |           |            |            |
| minhash.py        | pypy3       | `10.52s`   | `67.52s` | `266.74s` | `1060.77s` | `8278.96s` |
| minhash_m.py      | pypy3       | `7.87s`    | `51.07s` | `190.73s` | `859.66s`  | `4094.37s` |
| minhash_m_init.py | pypy3       | `7.56s`    | `52.22s` | `191.57s` | `680.1s`   | `5070.27s` |
| minhash_dss.py    | pypy3       | `5.33s`    | `22.19s` | `75.49s`  | `189.22s`  | `1019.88s` |
| minhash_v.py      | python3     | `3.06s`    | `4.19s`  | `6.19s`   | `13.51s`   | `59.42s`   |

![measurements](https://github.com/ppw0/minhash/blob/master/img/measurements.png)

# possible further ideas.

- C extensions.
- CUDA to further exploit parallelism.
- Locality Sensitive Hashing?
