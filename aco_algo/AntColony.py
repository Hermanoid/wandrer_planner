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
        self.network_graph = nx.MultiGraph(network_graph)

        # Add some fake nodes to the graph to represent "finishing" as an action
        # This way, each ant can decide whether to finish at a goal node or keep going.
        node_count = self.network_graph.number_of_nodes()
        self.finish_nodes = set()
        for goal_node in self.settings.goal_nodes:
            self.network_graph.add_node(node_count, **self.network_graph.nodes[goal_node])
            self.network_graph.add_edge(goal_node, node_count, length=0, traveled=False)
            self.finish_nodes.add(node_count)
            node_count += 1
        self.network_graph.graph["finish_nodes"] = self.finish_nodes
        nx.freeze(self.network_graph)
        nx.set_node_attributes(self.network_graph, {node: node in self.finish_nodes for node in self.network_graph.nodes}, 'is_finish_node')
        nx.set_edge_attributes(self.network_graph, 1, 'pheromone')

        print("Precomputing betweenness centrality")
        # Betweenness is used as a measure of how isolated a node is in the graph.
        # Isolated regions (like dead ends) tend to be overlooked by the algorithm
        #   because you generally have to travel them twice, in and out.
        # Deadendness is here to counteract that force and make sure you hit 
        #   dead ends the first time you go by them.
        k=min(1000, len(self.network_graph.nodes))
        self.betweenness_centrality = nx.betweenness_centrality(self.network_graph, weight='length', k=k)
        nx.set_node_attributes(self.network_graph, self.betweenness_centrality, 'betweenness_centrality')
        deadendness = {node: 1/1000*betweenness for node, betweenness in self.betweenness_centrality.items()}
        nx.set_node_attributes(self.network_graph, deadendness, 'deadendness')


        print("Precomputing shortest paths to goals")
        # Find the lengths of shortest paths from any goal to any node in the graph.
        # (Used as a more-accurate heuristic for the ant's goal-directedness)
        lengths = nx.multi_source_dijkstra_path_length(self.network_graph, self.settings.goal_nodes, weight='length')
        nx.set_node_attributes(self.network_graph, lengths, 'shortest_path_to_goal')

        print("Ant Colony Algo Init Done")

    def update_settings(self, settings: ACOSettings):
        self.settings = settings

    def run_iteration(self):
        print("Ant Colony Algo Run")

        # Do some stuff

        print("Ant Colony Algo Run Done")
