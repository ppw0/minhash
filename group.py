#!/usr/bin/python
# -*- coding: utf-8 -*-
# group.py: groups related items into lists.

# finding related items in a list of lists is finding connected components in a graph
import networkx
from networkx.algorithms.components.connected import connected_components

def to_edges(lst): # l is a list of lists
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

def igroup(related):
    return connected_components(to_graph(related)) # iterator
    
def group(related):
    return list(connected_components(to_graph(related)))
        
def print_groups(g): # print groups
    count = 0
    l = []
    for s in g:
        count += len(s)
        l.append(sorted(s))
    l.sort()
    for sublist in l:
        for el in sublist:
            print(str(el)+" ",end='')
        print("")
    print("%d elements in %d groups" %(count,len(g)))
    print("%d dupes" %(count-len(g)))
    
def print_groups_unordered(g):
    count = 0
    for s in g:
        count += len(s)
        for el in s:
            print(str(el)+" ",end='')
        print("")
    print("%d elements in %d groups" %(count,len(g)))
    print("%d dupes" %(count-len(g)))
    
def print_dupes(g): # prints all related items but one
    l = []
    count = 0
    for s in g:
        while len(s) > 1:
            l.append(s.pop())
            count += 1
    l.sort()
    for item in l:
        print(item)
    print("%d dupes" % (count))

def print_dupes_unordered(g):
    for s in g:
        while len(s) > 1:
            print(s.pop())

def print_stats(g):
    count = 0
    for s in g:
        count += len(s)
    print("%d elements in %d groups" %(count,len(g)))
    print("%d dupes" %(count-len(g)))