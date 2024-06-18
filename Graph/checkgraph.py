import networkx as nx


# Check if a graph is connected
def IfGraphConnect(G):
    # Choisir un noeud de départ arbitraire
    start_node = list(G.nodes)[0]

    # Créer un ensemble pour stocker les noeuds visités
    visited = set()

    # Créer une file d'attente pour le parcours en largeur
    queue = [start_node]

    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            queue.extend(set(G[node]) - visited)

    # Si tous les noeuds ont été visités, le graphe est connecté
    if len(visited) == len(G.nodes):
        print("The graph is connected")
    else:
        print("The graph is not connected")
    return


# Find the ACPM of a graph


def findACPM_Prim(G):
    # Initialisation des structures de données
    nodes = list(G.nodes(data=True))
    edges = list(G.edges(data=True))

    # Initialisation des nœuds visités et non visités
    visited = set()
    unvisited = {node[0] for node in nodes}

    # Choisir un nœud initial et l'ajouter à l'ensemble des nœuds visités
    current_node = nodes[0][0]
    visited.add(current_node)
    unvisited.remove(current_node)

    # Liste pour stocker les arêtes de l'ACPM
    mst_edges = []

    while unvisited:
        # Rechercher l'arête avec la durée minimum qui relie un nœud visité à un nœud non visité
        min_edge = None
        min_duration = float('inf')

        # Parcourir tous les nœuds visités
        for visited_node in visited:
            for unvisited_node, data in G[visited_node].items():
                duration = data.get('duration', float('inf'))
                # Si le nœud non visité est dans l'ensemble des nœuds non visités et que la durée est inférieure à la durée minimale trouvée jusqu'à présent
                # En ne sélectionnant que les nœuds non visités lors de l'ajout des arêtes, vous vous assurez qu'aucun cycle n'est créé.
                if unvisited_node in unvisited and duration < min_duration:
                    min_edge = (visited_node, unvisited_node, duration)
                    min_duration = duration

        if min_edge:
            # Ajouter l'arête trouvée à l'ACPM
            mst_edges.append(min_edge)

            # Mettre à jour les ensembles de nœuds visités et non visités
            _, unvisited_node, _ = min_edge
            visited.add(unvisited_node)
            unvisited.remove(unvisited_node)

    # Construire le graphe de l'ACPM
    acpm_graph = nx.Graph()

    # Ajouter les nœuds avec leurs attributs
    for node, attr in nodes:
        acpm_graph.add_node(node, **attr)

    # Ajouter les arêtes avec la durée
    for visited_node, unvisited_node, duration in mst_edges:
        acpm_graph.add_edge(visited_node, unvisited_node, duration=duration)




    return acpm_graph