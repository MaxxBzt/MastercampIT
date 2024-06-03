
# # format pour les sommets :
# V num_sommet nom_sommet numéro_ligne si_terminus branchement (0 stations en commun, 1 pour la direction 1,  2 pour la direction 2, ainsi
#   de suite ...)
#
# # format pour les arrêtes :
# E num_sommet1 num_sommet2 temps_en_secondes

import networkx as nx
def dataversion1():
    print("Data version 1")
    file = open("Version1/metro.txt", "r", encoding ='utf-8')
    # start at line 15
    for i in range(15):
        file.readline()
    # Create all the nodes
    G = nx.Graph()
    for line in file:
        if line[0] == 'V':
            # remove \n
            line = line[:-1]
            # remove V
            line = line[2:]
            line = line.split(";")
            name_stop = line[0].strip().split()[1:]
            name_stop = ' '.join(name_stop)
            G.add_node(int(line[0].split(" ")[0]),name=name_stop,ligne=str(line[1]).strip(),if_terminus=bool(line[2].split(" ")[0].strip()),branchement=int(line[2].split(" ")[1]))

        # Create all the edges
        if line[0] == 'E':
            line = line.split()
            G.add_edge(int(line[1]), int(line[2]), duration=int(line[3]))


    return G

G = dataversion1()
for i in G.nodes:
    print(G.nodes[i])

#Display the "station 1 -> station 2 duration : " for each edge
for edge in G.edges:
    print("station",G.nodes[edge[0]]['name'],"-> station",G.nodes[edge[1]]['name'],"duration :",G.edges[edge]['duration'])


