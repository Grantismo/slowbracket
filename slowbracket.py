from urllib.request import urlopen
import json
import networkx as nx
import matplotlib.pyplot as plt
import os
os.add_dll_directory("C:/Program Files/Graphviz/bin")
import pygraphviz


# JSON structure 

# sets
#   id 
#   completedAt
#   entrant1Id
#   entrant2Id

# seeds
#   id
#   entrantId
#   mutations
#       participants
#           [id]
#               gamerTag
#       players
#           [id]
#               gamerTag

# graph structure
# node = set id
# edge = set(entrant[12]Id) -> set id

def read_json_url(url):
    resp = urlopen(url)
    return json.loads(resp.read())

def set_end(s):
    if s['completedAt']:
        return s['completedAt']
    return s['createdAt'] 

def build_graph(entrants, sets):
    g = nx.DiGraph()
    g.graph['graph']={'rankdir':'LR'}
    sets = [s for s in sets if s['entrant1Id'] and s['entrant2Id']] # remove empty sets
    g.add_nodes_from([s['id'] for s in sets])
    sorted_sets = sorted(sets, key=set_end) 
    for entrant in entrants:
        sets = [s for s in sorted_sets if entrant['entrantId'] in set([s['entrant1Id'], s['entrant2Id']])]
        cur_set = sets[0]
        for s in sets:
            if cur_set['id'] == s['id']:
                continue
            g.add_edge(cur_set['id'], s['id'], duration=s['completedAt'] - cur_set['completedAt'])
            cur_set = s
    return g

def get_set_labels(entrants, sets):
    labels = {} # set id -> label
    entrant_labels = {} # entrantId -> label
    for entrant in entrants:
        entrant_labels[entrant['entrantId']] = [players]


doubles = read_json_url('https://api.smash.gg/phase_group/1803504?expand[]=sets&expand[]=seeds')
# singles = read_json_url('https://api.smash.gg/phase_group/1803505?expand[]=sets&expand[]=seeds')

doubles_entrants = doubles['entities']['seeds']
doubles_sets = doubles['entities']['sets']
doubles_graph = build_graph(doubles_entrants, doubles_sets)
print(get_set_labels(doubles_entrants, doubles_sets))

a = nx.nx_agraph.to_agraph(doubles_graph)
a.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8 ')
a.draw('test.png')
