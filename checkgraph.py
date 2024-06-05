import networkx as nx
# Check if a graph is connected
def IfGraphConnect(G):
    if nx.is_connected(G):
        print("The graph is connected")
        return True
    else:
        print("The graph is not connected")
        return False


# Find the ACPM of a graph
def findACPM(G):
    if not IfGraphConnect(G):
        return
    # Find the minimum spanning tree of the graph
    ACPM = nx.minimum_spanning_tree(G)
    return ACPM

