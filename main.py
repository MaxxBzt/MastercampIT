import matplotlib.pyplot as plt
import customtkinter as ctk


print("Hello world")
import networkx as nx
G = nx.Graph()

G.add_node(1,name="Abesses",ligne=12,if_terminus=False,branchement=0)
G.add_node(3,name="Alésia",ligne=4,if_terminus=False,branchement=0)

print(G.nodes[1])




G.add_edge(1, 3, duration=2)

G.number_of_nodes()
G.number_of_edges()
print(list(G.nodes))
print(list(G.edges))


