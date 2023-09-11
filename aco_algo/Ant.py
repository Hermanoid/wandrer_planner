import networkx as nx
from ACOSettings import ACOSettings
import numpy as np

class Ant:
    def __init__(self, network_graph: nx.MultiGraph, settings: ACOSettings):
        self.network_graph = network_graph
        self.update_settings(settings)
        self.traveled_edges = set()
        self.traveled_length = 0
    
    def update_settings(self, settings: ACOSettings):
        self.settings = settings
        self.goal_locs = [self.network_graph[node]["proj_pos"] for node in self.settings.goal_nodes]
    
    def edge_sort(self, edge):
        return (edge[0], edge[1]) if edge[0] < edge[1] else (edge[1], edge[0])

    def run(self):
        current_node = self.settings.start_node
        self.route = [current_node]
        self.traveled_edges = set()
        self.traveled_length = 0
        while current_node not in self.settings.goal_nodes:
            outgoing_edges = self.network_graph.edges(current_node, data=True)
            desireability = np.array(self.desireability(edge) for edge in outgoing_edges)
            desireability = desireability / np.sum(desireability)
            chosen_edge = np.random.choice(outgoing_edges, p=desireability)

            current_node = chosen_edge[1]
            self.route.append(current_node)
            self.traveled_edges.add(self.edge_sort(chosen_edge))
            self.traveled_length += chosen_edge[2]['length']

        return self.route
        
    def desireability(self, edge):
        """
        Calculates the desireability of an edge for the ant.
        Includes pheromone and heuristic information.
        """
        pheromone = edge[2]['pheromone']
        end_node = self.network_graph.nodes[edge[1]]
        length = edge[2]['length']
        heuristic = 0
        heuristic += end_node['deadendness'] * self.settings.deadendness_factor
        if self.settings.directional_factor > 0:
            dist_to_goal = np.min(np.linalg.norm(self.goal_locs - end_node["proj_pos"], axis=1))
            remaining_dist = max(self.settings.target_length - self.traveled_length - length, 0)
            # Point the ant in the right direction according to abs(remaining-dist_to_goal)
            # This value wil be greater if this goal gets closer to how far from the goal the ant should be
            # if the ant is at the start, remaining will be large, so goals farther from the start will be more desireable
            # this quantity should be "indexed" off alternative arcs.

        traveled = edge[2]['traveled'] or self.edge_sort(edge) in self.traveled_edges
        return pheromone**self.settings.pheromone_weight * \
            heuristic**self.settings.heuristic_weight * \
            (self.settings.traveled_factor if traveled else 1)