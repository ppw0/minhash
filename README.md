# minhash
- `group.py` helper module
- `seqmatch.py` uses sequence matching to find similar text files
    - `seqmatch_m.py` is the multithreaded version
- `minhash.py` uses MinHash and Jaccard similarity estimation algorithms, based on http://mccormickml.com/2015/06/12/minhash-tutorial-with-python-code/ 
    - `minhash_m.py` is the multiprocessing version, with shared memory access and simplified data structures (Unix only)
        - `minhash_m_init.py` is Windows-compatible; uses an initializer to preserve global variable states https://medium.com/@rvprasad/data-and-chunk-sizes-matter-when-using-multiprocessing-pool-map-in-python-5023c96875ef
        - `minhash_dss.py` uses delimited search space
        - `minhash_v.py` is the vectorized version; the use of an initializer avoids synchronization stalls and memory bubbles with large inputs. Unix only, as changes to the NumPy array do not get carried back to the main process in Windows

# lessons learned
- a simple heuristic can significantly decrease running time while still finding a large majority of similar files
- if the input iterator is very large, using `map` will lead to a segmentation fault
- if a function returns results faster than they can be consumed, using it with `imap` and `imap_unordered` will cause a memory bubble
    - https://stackoverflow.com/questions/40922526/memory-usage-steadily-growing-for-multiprocessing-pool-imap-unordered
    - https://stackoverflow.com/questions/9862091/iteration-over-pool-imap-unordered
- `pypy3` is significantly faster than `python3`, but it did not support Numba
- minimize your inputs before passing them off to a function (e.g. grouping results uses `connected_components` from `networkx` which had high space complexity)
- vectorize, if possible

# measurements
a random selection of non-duplicate text files of varying sizes (0-1767kb):

|        script       |  interpreter  | 1500       | 5000     |   10000   |   20000    |    50000   |
| :------------------ | ------------- | :--------- | :------- | :-------- | :--------- | :--------- |
| `seqmatch.py`       | `python3`     | `2503.13s` |          |           |            |            |
| `seqmatch_m.py`     | `python3`     | `658.70s`  |          |           |            |            |
| `minhash.py`        | `pypy3`       | `10.52s`   | `67.52s` | `266.74s` | `1060.77s` | `8278.96s` |
| `minhash_m.py`      | `pypy3`       | `7.87s`    | `51.07s` | `190.73s` | `859.66s`  | `4094.37s` |
| `minhash_m_init.py` | `pypy3`       | `7.56s`    | `52.22s` | `191.57s` | `680.1s`   | `5070.27s` |
| `minhash_dss.py`    | `pypy3`       | `5.33s`    | `22.19s` | `75.49s`  | `189.22s`  | `1019.88s` |
| `minhash_v.py`      | `python3`     | `3.06s`    | `4.19s`  | `6.19s`   | `13.51s`   | `59.42s`   |

![measurements](https://github.com/ppw0/minhash/blob/master/img/measurements.png)
