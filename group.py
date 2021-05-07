#!/usr/bin/python3
# -*- coding: utf-8 -*-
# group.py: groups related items together.

# finding common items in a group of lists is finding connected components in a graph
import networkx
from networkx.algorithms.components.connected import connected_components

def to_edges(lst):
    it = iter(lst)
    last = next(it)
    for current in it:
        yield last, current
        last = current

def to_graph(lst):
    G = networkx.Graph()
    for sublist in lst: # treat each sublist as a complete graph
        G.add_nodes_from(sublist)
        G.add_edges_from(to_edges(sublist))
    return G

def igroup(lst):
    return connected_components(to_graph(lst))
    
def group(lst):
    return list(igroup(lst))

def print_groups(g):
    l = [sorted(s) for s in g]
    l.sort()
    for sublist in l:
        for el in sublist:
            print(str(el)+" ",end='')
        print("")
    print_stats(g)
    
def print_groups_unordered(g):
    for sublist in g:
        for el in sublist:
            print(str(el)+" ",end='')
        print("")
    
def print_dupes(g):
    count = sum(len(s) for s in g)
    l = []
    for s in g:
        while len(s) > 1:
            l.append(s.pop())
    l.sort()
    map(print,l)
    print("%d dupes" % (count))

def print_dupes_unordered(g):
    for s in g:
        while len(s) > 1:
            print(s.pop())

def print_stats(g):
    count = sum(len(s) for s in g)
    print("%d elements in %d groups, %d dupes" %(count,len(g),count-len(g)))