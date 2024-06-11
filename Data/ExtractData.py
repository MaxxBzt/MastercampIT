from Graph.shortestpath import *

# # format pour les sommets :
# V num_sommet nom_sommet numéro_ligne si_terminus branchement (0 stations en commun, 1 pour la direction 1,  2 pour la direction 2, ainsi
#   de suite ...)
#
# # format pour les arrêtes :
# E num_sommet1 num_sommet2 temps_en_secondes

from Graph.checkgraph import *


def dataversion1():
    print("Data version 1")
    file = open("../Version1/metro.txt", "r", encoding ='utf-8')
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

    file.close()
    #print(G)
    #print(G.nodes)
    #print(G.edges)

    return G


def dataversion2():
    # First we determine the RATP Agency thanks to agency.txt
    ratp = "IDFM:Operator_100"

    # We determine all the lines metro operated by the RATP thanks to routes.txt
    # Reminders : it's metro if the route_type is 1
    file = open("../Version2_Version3/data/routes.txt", "r")
    metro_lines = {}
    # We don't take in consideration the first line

    for line in file:
        line = line.split(",")
        if ratp in line and line[5] == "1":
            metro_lines[line[0]] = line[2]

    file.close()


    print("Data version 2")
    print("Lines operated by the RATP :")
    print(metro_lines)

    # Now we determine the directions for all lines
    directions = {}

    # We determine the directions for all lines thanks to trips_filtered.txt
    file = open("../Version2_Version3/data/trip_id_filtered.txt", "r")

    # For each trip_id of the text trip_id_filtered.txt we determine the direction
    for line in file:
        if line == " ":
            continue
        line = line.split(",")
        # if the route id is a line of metro in metro_lines
        if line[0] in metro_lines.keys():
            value = metro_lines.get(line[0])
            if value not in directions:
                directions[value] = [[line[3], line[2]]]
            else:
                # Check if the direction is not already in the list for the line
                if not any(item[0] == line[3] for item in directions[value]):
                    directions[value].append([line[3], line[2]])

    print(directions)

    # Now we determine the stops for all lines
    stops = {}

    # Thanks to stop_times_filtered.txt we determine the stops for all lines and their duration
    # To do so, we have for each trip_id the stops and at what time the metro stops at each stop
    file = open("../Version2_Version3/data/stop_times_filtered.txt", "r")




dataversion1()
test = dijkstra(dataversion1(), 1,25)
print(test)
print("The shortest path is:")
print(test[0])
print("The duration of the shortest path is:")
# Convertir secondes en minutes
print(test[1]//60,"minutes",test[1]%60,"secondes")

dataversion2()

'''
G = dataversion1()
for i in G.nodes:
    #print(G.nodes[i])
    pass

#Display the "station 1 -> station 2 duration : " for each edge
for edge in G.edges:
    #print("station",G.nodes[edge[0]]['name'],"-> station",G.nodes[edge[1]]['name'],"duration :",G.edges[edge]['duration'])
    pass

# Create a dictionary mapping line numbers to colors
line_colors = {
    '1': 'blue',
    '2': 'red',
    '3': 'green',
    '4': 'purple',
    '5': 'orange',
    '6': 'brown',
    '7': 'pink',
    '8': 'gray',
    '9': 'olive',
    '10': 'cyan',
    '11': 'magenta',
    '12': 'yellow',
    '13': 'black',
    '14': 'lime',
}

# Initialize an empty list for edge colors
edge_colors = []

# Iterate over each edge in the graph
for edge in G.edges:
    # Get the line attribute of the first node of the edge
    line = G.nodes[edge[0]]['ligne']
    # Use the line attribute to look up the corresponding color in the dictionary
    color = line_colors.get(line, 'black')  # Default to black if line number is not in the dictionary
    # Append the color to the edge colors list
    edge_colors.append(color)

# Draw the graph with edge colors
nx.draw(G, with_labels=False, node_size=100, edge_color=edge_colors)
plt.show()

# check if the graph is connected
IfGraphConnect(G)

# Find the ACPM of the graph
ACPM = findACPM(G)
print("The ACPM of the graph is:")
print(ACPM.edges)
nx.draw(ACPM, with_labels=False, node_size=100, edge_color=edge_colors)
plt.show()
'''
