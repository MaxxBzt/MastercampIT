def dijkstra(graph, start, end):
    # Initialise un dico avec la station et la distance entre les deux (inf au depart)
    distances = {node: float('inf') for node in graph.nodes}

   # La distance entre le depart et lui-même est 0
    distances[start] = 0

    # Initialise un dico avec par quel station passer
    previous_nodes = {node: None for node in graph.nodes}

    # Initialise un dico pour garder la trace des lignes utilisées
    used_lines = {node: [] for node in graph.nodes}


    # Crée une liste avec toutes les stations à explorer
    queue = list(graph.nodes)
    print(queue)

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

            # Récupère la ligne de métro (assumant qu'il y a un attribut 'line')
            line = attributes.get('line', None)

            # Si on a déjà utilisé cette ligne, on la saute
            if line in used_lines[current_node]:
                continue


            # Si la distance est plus petite que la distance actuelle, on met à jour la distance
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                used_lines[neighbor] = used_lines[current_node] + [line]


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

    return path, duree

