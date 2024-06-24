from networkx import is_directed

from Graph.shortestpath import *

# # format pour les sommets :
# V num_sommet nom_sommet numéro_ligne si_terminus branchement (0 stations en commun, 1 pour la direction 1,  2 pour la direction 2, ainsi
#   de suite ...)
#
# # format pour les arrêtes :
# E num_sommet1 num_sommet2 temps_en_secondes

from Graph.checkgraph import *
from matplotlib import pyplot as plt


def dataversion1():
    #print("Data version 1")
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

    file.close()
    #print(G)
    #print(G.nodes)
    #print(G.edges)
    #for station_id, data in G.nodes(data=True):
        #print(f"Station ID: {station_id}, Name: {data['name']}, Metro Line: {data['ligne']}")

    return G


def merge_stations(G):
    # We need to merge the nodes with the same name
    nodes = list(G.nodes)
    i = 0
    while i < len(nodes):
        node = nodes[i]
        for j in range(i + 1, len(nodes)):
            node2 = nodes[j]
            if G.nodes[node]['name'] == G.nodes[node2]['name']:
                # We merge the nodes
                G = nx.contracted_nodes(G, node, node2, self_loops=False)
                nodes = list(G.nodes)  # Update the list of nodes
                break
        else:
            i += 1  # Only increment i if no nodes were merged in the inner loop
    return G

def dataversion2():
    # First we determine the RATP Agency thanks to agency.txt
    ratp = "IDFM:Operator_100"

    # We determine all the lines metro operated by the RATP thanks to routes.txt
    # Reminders : it's metro if the route_type is 1
    file = open("Version2_Version3/data/routes.txt", "r")
    metro_lines = {}
    # We don't take in consideration the first line

    for line in file:
        line = line.split(",")
        if ratp in line and line[5] == "1":
            metro_lines[line[0]] = line[2]

    file.close()


    # Now we determine the directions for all lines
    directions = {}

    # We determine the directions for all lines thanks to trips_filtered.txt
    file = open("Version2_Version3/data/trip_id_filtered.txt", "r", encoding="utf-8")

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

    file = open("Version2_Version3/data/stop_times_filtered.txt", "r", encoding="utf-8")

    stops = {} # { 1 : [ trip 1 : [[stop_id, stop_name, line, time, wheelchair],[stop_id, stop_name, line, time, wheelchair]], trip 2 : [[....]], 2 : [[stop_id, stop_name, line, time, wheelchair],[stop_id, stop_name, line, time, wheelchair]]}

    for direction in directions.values():
        file.seek(0)  # Reset the cursor to the start of the file
        name_to_id = {}  # Maps station names to IDs for each line separately
        for line in file:
            line = line.split(",")
            for element in direction:
                if element[1] == line[0]:
                    line_metro = get_key_from_value(line, directions)
                    stop_name = searchstop(line[3])
                    stop_id = line[3]
                    # If the station name already exists in this line, use the existing ID
                    if stop_name[2] in name_to_id:
                        stop_id = name_to_id[stop_name[2]]
                    else:
                        # Otherwise, map the station name to the new ID
                        name_to_id[stop_name[2]] = stop_id
                    if element[1] not in stops:
                        stops[element[1]] = [[stop_id, stop_name[2], line_metro, line[1], stop_name[12], [stop_name[4],
                                                                                                          stop_name[
                                                                                                              5]]]]  # [stop_id, stop_name, line, time, wheelchair, coordinates]
                    else:
                        stops[line[0]].append([stop_id, stop_name[2], line_metro, line[1], stop_name[12], [stop_name[4],
                                                                                                           stop_name[
                                                                                                               5]]])  # [stop_id, stop_name, line, time, wheelchair, coordinates]

    #print(stops)

    # Create the graph
    G = nx.DiGraph()

    for trip, stop in stops.items():
        for i in range(len(stop) - 1):
            if not G.has_node(stop[i][0]):
                G.add_node(stop[i][0], name=stop[i][1], ligne=stop[i][2], branchement=0, wheelchair=stop[i][4],
                           coordinates=tuple(map(float, stop[i][5])))
            if not G.has_node(stop[i + 1][0]):
                G.add_node(stop[i + 1][0], name=stop[i + 1][1], ligne=stop[i + 1][2], branchement=0,
                           wheelchair=stop[i + 1][4], coordinates=tuple(map(float, stop[i + 1][5])))

            # Store all the direction of the line
            terminus = directions[stop[i][2]]
            #print(terminus)
            # Verify if the edge already exists
            if not G.has_edge(stop[i][0], stop[i + 1][0]):
                # we will choose directed edges to avoid pb with the directions
                if len(terminus) >=3:
                    G.add_edge(stop[i][0], stop[i + 1][0],name=stop[i][1] + "-" + stop[i + 1][1], duration=time_difference(stop[i][3], stop[i + 1][3]))
                    G.add_edge(stop[i+1][0], stop[i][0], name=stop[i+1][1] + "-" + stop[i][1],
                               duration=time_difference(stop[i][3], stop[i + 1][3]))
                else :
                    G.add_edge(stop[i][0], stop[i + 1][0], name=stop[i][1] + "-" + stop[i + 1][1],
                               duration=time_difference(stop[i][3], stop[i + 1][3]))

        # We are going to add the transfers
        # We determine the transfers thanks to transfers.txt

    file = open("Version2_Version3/data/transfers.txt", "r", encoding="utf-8")


    #Permet de connecter le graph
    for line in file:
        line = line.split(",")
        # Compare the stop_id with the nodes of the graph
        if line[0] in G.nodes and line[1] in G.nodes:
            duration = int(line[3])  # en seconde
            round(duration, 2)
            if not G.has_edge(line[0], line[1]) and not G.has_edge(line[1], line[0]):
                # Create the new edges with the transfer
                G.add_edge(line[0], line[1], name="transfer", duration=duration)
                G.add_edge(line[1], line[0], name="transfer", duration=duration)

    # if a node is connected to an another node which not belong to the same line, we increment the branchement attribute
    for node in G.nodes:
        for edge in G.edges:
            if edge[0] == node:
                if G.nodes[edge[1]]['ligne'] != G.nodes[node]['ligne']:
                    G.nodes[node]['branchement'] += 1

    file.close()

    # verify if the graph is directed
    #print(is_directed(G))


    #for node in G.nodes:
        #print("node", node, "name", G.nodes[node]['name'], "branchement", G.nodes[node]['branchement'])

    connected = IfGraphConnect(G)

    pos = {}
    for node in G.nodes:
        pos[node] = G.nodes[node]['coordinates']

    # The label to be the name of the station
    labels = {}
    for node in G.nodes:
        labels[node] = G.nodes[node]['name']

    #  the edges with the name tranfer is in red

    edge_colors = []
    for edge in G.edges:
        if G.edges[edge]['name'] == "transfer":
            edge_colors.append("red")
        else:
            edge_colors.append("black")


    # display the graph

    nx.draw(G, pos, with_labels=False, node_size=10, edge_color=edge_colors)
    # Draw the labels
    nx.draw_networkx_labels(G, pos, labels, font_size=5)


    #plt.show()

    return G


def searchstop(stop_id):
    stops_file = open("Version2_Version3/data/stops.txt", "r")
    for stops in stops_file:
        stops = stops.split(",")
        if stops[0] == stop_id:
            stops_file.close()
            return stops
    stops_file.close()
    return None

def get_key_from_value(line, dictionary):
    for key, value in dictionary.items():
        for item in value:
            if line[0] == item[1]:  # comparing with the second element of the list
                return key  # return the key where we find the value
    return None  # return None if no match is found


def time_difference(time1, time2):
    # if the time start with something >= 24, we remove 24 to have a time between 0 and 24
    if int(time1.split(":")[0]) >= 24:
        time1 = str(int(time1.split(":")[0]) - 24) + ":" + time1.split(":")[1] + ":" + time1.split(":")[2]
    if int(time2.split(":")[0]) >= 24:
        time2 = str(int(time2.split(":")[0]) - 24) + ":" + time2.split(":")[1] + ":" + time2.split(":")[2]
    time1 = time1.split(":")
    time2 = time2.split(":")

    time = (int(time2[0]) - int(time1[0])) * 3600 + (int(time2[1]) - int(time1[1])) * 60 + (int(time2[2]) - int(time1[2]))
    if time < 0:
        time = time *-1

    return round(time) # en secondes




#dataversion1()
#test = dijkstra(dataversion1(), 1,25)
#print(test)
#print("The shortest path is:")
#print(test[0])
#print("The duration of the shortest path is:")
# Convertir secondes en minutes
#print(test[1]//60,"minutes",test[1]%60,"secondes")

#dataversion2()

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
