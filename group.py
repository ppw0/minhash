#!/usr/bin/python3
# -*- coding: utf-8 -*-
# group.py

import networkx as nx
import more_itertools
from networkx.algorithms.components.connected import connected_components

def group(lst):
    G = nx.Graph()
    G.add_nodes_from(more_itertools.flatten(lst))
    for x in lst:
        G.add_edges_from(more_itertools.pairwise(x))
    return list(connected_components(G))

def print_complete(g):
    g = group(g)
    count = sum(len(x) for x in g)
    for x in g:
        print(*x, sep='\n')
        print("---")
    print("%d elements in %d groups" %(count,len(g)))
