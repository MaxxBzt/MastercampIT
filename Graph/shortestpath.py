def dijkstra(graph, start, end):
    # Initialise un dico avec la station et la distance entre les deux (inf au depart)
    distances = {node: float('inf') for node in graph.nodes}

   # La distance entre le depart et lui-même est 0
    distances[start] = 0

    # Initialise un dico avec par quel station passer
    previous_nodes = {node: None for node in graph.nodes}

    # Crée une liste avec toutes les stations à explorer
    queue = list(graph.nodes)
    #print(queue)

    while queue:
        # Tant qu'on a des stations à explorer

        # Trouver le nœud avec la plus petite distance et on l'enlève de la liste à explorer
        current_node = min(queue, key=lambda node: distances[node])
        queue.remove(current_node)

        # Si la distance entre le noeud actuel et le noeud de départ est infinie, on arrête
        if distances[current_node] == float('inf'):
            break

        # Si on est arrivé à la station d'arrivée, on arrête
        if current_node == end:
            break

        # Pour chaque voisin de la station actuelle à explorer
        for neighbor, attributes in graph[current_node].items():
            # On regarde le poids de l'arête entre la station actuelle et le voisin
            weight = attributes.get('weight', 1)
            # On ajoute au trajet entier la distance avec la prochaine station
            distance = distances[current_node] + weight

            # Si la distance est plus petite que la distance actuelle, on met à jour la distance
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node

    # On crée le chemin entre la station de départ et la station d'arrivée
    path = []
    node = end
    while previous_nodes[node] is not None:
        # On ajoute la station à la liste du chemin
        path.insert(0, node)
        node = previous_nodes[node]
    if path:
        # On ajoute la station de départ
        path.insert(0, start)

    # On retrouve la distance totale en secondes grâce aux weights des edges
    duree = 0
    for i in range(len(path)-1):
        duree += graph[path[i]][path[i+1]]['duration']

        # Initialize result list for path with line change information
    path_with_line_change = []

    # Mark nodes where there is a change in metro lines
    for i in range(len(path)):
        current_node = path[i]
        if i == 0:
            path_with_line_change.append((current_node, False, graph.nodes[current_node]['ligne']))  # Starting point, no change initially
        else:
            previous_node = path[i - 1]
            current_line = graph.nodes[current_node]['ligne']
            previous_line = graph.nodes[previous_node]['ligne']

            if current_line != previous_line:
                path_with_line_change.append((current_node, True, graph.nodes[current_node]['ligne']))
            else:
                path_with_line_change.append((current_node, False, graph.nodes[current_node]['ligne']))

    return path_with_line_change, duree


def bellman_ford(graph, start, end):
    # Step 1: Prepare the distance for each node
    distance = {node: float('inf') for node in graph.nodes}
    distance[start] = 0

    # Step 2: Relax edges repeatedly
    for _ in range(len(graph.nodes) - 1):
        for node in graph.nodes:
            for neighbour, attributes in graph[node].items():
                weight = attributes.get('weight', 1)
                if distance[node] != float('inf') and distance[node] + weight < distance[neighbour]:
                    distance[neighbour] = distance[node] + weight

    # Step 3: Check for negative-weight cycles
    for node in graph.nodes:
        for neighbour, attributes in graph[node].items():
            weight = attributes.get('weight', 1)
            if distance[node] != float('inf') and distance[node] + weight < distance[neighbour]:
                raise ValueError("Graph contains a negative-weight cycle")

    # Step 4: Path reconstruction
    path = []
    current_node = end
    while current_node is not None:
        path.insert(0, current_node)
        current_node = next((node for node, neighbour in graph[current_node].items() if distance[node] + neighbour.get('weight', 1) == distance[current_node]), None)

    return path