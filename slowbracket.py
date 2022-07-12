from urllib.request import urlopen
import json
import networkx as nx
import matplotlib.pyplot as plt
import os
import datetime
os.add_dll_directory('C:/Program Files/Graphviz/bin')
import pygraphviz
import itertools
from collections import defaultdict

# add dubs to graph

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

def remove_empty_sets(sets):
    return [s for s in sets if s['entrant1Id'] and s['entrant2Id']] # remove empty sets

def build_graph(entrants, sets):
    g = nx.DiGraph()
    g.graph['graph']={'rankdir':'LR'}
    labels = get_set_labels(entrants, sets)
    g.add_nodes_from([labels[s['id']] for s in sets])
    sorted_sets = sorted(sets, key=set_end) 
    players = set([])
    player2Entrant = defaultdict(set)
    for entrant in entrants:
        for p in entrant['mutations']['players'].values():
            players.add(p['id'])
            player2Entrant[p['id']].add(entrant['entrantId'])

    for player in players:
        sets = [s for s in sorted_sets if not set([s['entrant1Id'], s['entrant2Id']]).isdisjoint(player2Entrant[player])]
        if sets:
            cur_set = sets[0]
            for s in sets:
                if cur_set['id'] == s['id']:
                    continue
                duration = s['completedAt'] - cur_set['completedAt']
                g.add_edge(labels[cur_set['id']], labels[s['id']], duration=duration, label=str(datetime.timedelta(seconds=duration)))
                cur_set = s
    return g

def get_entrant_label(players):
    if len(players) == 0:
        return ''
    players_values = list(players.values())
    if len(players) == 1:
        return players_values[0]['gamerTag']
    return players_values[0]['gamerTag'] + ' / ' + players_values[1]['gamerTag']


def get_set_labels(entrants, sets):
    labels = {} # set id -> label
    entrant_labels = {} # entrantId -> label
    for entrant in entrants:
        entrant_labels[entrant['entrantId']] = get_entrant_label(entrant['mutations']['players'])
    for s in sets:
        if not s['entrant1Id'] and not s['entrant2Id']:
            label = ''
        elif not s['entrant1Id'] or not s['entrant2Id']:
            label = entrant_labels[s['entrant1Id'] or s['entrant2Id']] + ' bye'
        else:
            label = entrant_labels[s['entrant1Id']] + ' vs. ' + entrant_labels[s['entrant2Id']]
        labels[s['id']] = s['midRoundText'] + ": " + label
    return labels


doubles = read_json_url('https://api.smash.gg/phase_group/1803505?expand[]=sets&expand[]=seeds')
singles = read_json_url('https://api.smash.gg/phase_group/1803504?expand[]=sets&expand[]=seeds')

doubles_entrants = doubles['entities']['seeds']
doubles_sets = remove_empty_sets(doubles['entities']['sets'])
singles_entrants = singles['entities']['seeds']
singles_sets = remove_empty_sets(singles['entities']['sets'])
doubles_graph = build_graph(doubles_entrants + singles_entrants, doubles_sets + singles_sets)
for match in sorted(doubles_graph.edges(data=True), key=lambda e: e[2]['duration'], reverse=True):
    print(match[2]['label'] + ": " + match[0] + " -> " +  match[1])

a = nx.nx_agraph.to_agraph(doubles_graph)
a.layout('dot', args="-Nfontsize=10 -Nwidth='.5' -Nheight='.5' -Nmargin=0 -Gfontsize=8 -Gnodesep=.6 -Gsplines=true -Gsep='+25,25'")
a.draw('test.png')
