import networkx as nx
import numpy as np
from .ACOSettings import ACOSettings


class AntColony():
    def __init__(self, network_graph: nx.MultiGraph, initial_settings: ACOSettings):
        """
        Construct a new Ant Colony for holding the network graph and settings.
        Warning: the provided network graph is modified in place to include all sorts of attributes.
        """
        print("Ant Colony Algo Init")
        self.settings = initial_settings
        self.network_graph = network_graph
        nx.set_edge_attributes(self.network_graph, 0, 'pheromone')

        print("Precomputing betweenness centrality")
        self.betweenness_centrality = nx.betweenness_centrality(self.network_graph, weight='length')
        nx.set_node_attributes(self.network_graph, self.betweenness_centrality, 'betweenness_centrality')
        
        print("Precomputing other stuff")
        deadendness = {node: 1/1000*betweenness for node, betweenness in self.betweenness_centrality.items()}
        nx.set_node_attributes(self.network_graph, deadendness, 'deadendness')

        print("Ant Colony Algo Init Done")

    def update_settings(self, settings: ACOSettings):
        self.settings = settings

    def run_iteration(self):
        print("Ant Colony Algo Run")

        # Do some stuff

        print("Ant Colony Algo Run Done")
