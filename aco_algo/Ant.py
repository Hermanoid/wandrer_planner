import networkx as nx
from .ACOSettings import ACOSettings
import numpy as np

class Ant:
    def __init__(self, network_graph: nx.MultiGraph, settings: ACOSettings):
        self.network_graph = network_graph
        self.finish_nodes = network_graph.graph["finish_nodes"]
        self.update_settings(settings)
        self.traveled_edges = set()
        self.traveled_length = 0
    
    def update_settings(self, settings: ACOSettings):
        self.settings = settings
        self.goal_locs = [self.network_graph.nodes[node]["proj_pos"] for node in self.settings.goal_nodes]
    
    def edge_sort(self, edge):
        return (edge[0], edge[1]) if edge[0] < edge[1] else (edge[1], edge[0])

    def run(self):
        current_node = self.settings.start_node
        self.route = [current_node]
        self.traveled_edges = set()
        self.traveled_length = 0
        while current_node not in self.settings.goal_nodes:
            outgoing_edges = self.network_graph.edges(current_node, data=True)
            desireabilities = self.desireabilities(outgoing_edges)
            desireabilities = desireabilities / np.sum(desireabilities)
            chosen_edge = np.random.choice(outgoing_edges, p=desireabilities)

            current_node = chosen_edge[1]
            self.route.append(current_node)
            self.traveled_edges.add(self.edge_sort(chosen_edge))
            self.traveled_length += chosen_edge[2]['length']

        return self.route

    def calc_dist_diff(self, edge):
        """
        Dist diff is used to help the ant in the right direction according to abs(remaining-to_goal)
        This value wil be greater if this goal gets closer to how far from the goal the ant should be
        if the ant is at the start, remaining will be large, so goals farther from the start will be more desireable
        this heuristic is measured relative to the other arc options

        """
        to_goal = self.network_graph.nodes[edge[1]]["shortest_path_to_goal"]
        length = edge[2]['length']
        remaining_dist = max(self.settings.target_length - self.traveled_length - length, 0)
        
        return abs(remaining_dist - to_goal)
        
    def desireabilities(self, edges):
        """
        Calculates the desireability of an edge for the ant.
        Includes pheromone and heuristic information.
        """
        end_nodes = [self.network_graph.nodes[edge[1]] for edge in edges]
        heuristics = np.zeros(shape=(len(edges),), dtype=float)

        # Add a boost for going towards/away from the goal
        # The correct direction is based purely on traveled distance and distance remaining to goal.
        if self.settings.directional_coeff > 0:
            # Calculate dist diffs (see function comment)
            dist_diffs = np.array([self.calc_dist_diff(edge) for edge in edges])
            # Normalize diffs for relative comparison
            dist_diffs = (dist_diffs - np.mean(dist_diffs)) / np.std(dist_diffs)
            # Smack it with a sigmoid (https://eelslap.com/)
            dist_diffs = 1 / (1 + np.exp(-dist_diffs))
            # Finally, scale and add to heuristics
            heuristics += dist_diffs * self.settings.directional_coeff

        # Add a boost for deadend-ier nodes
        heuristics += np.array([end_node['deadendness'] for end_node in end_nodes]) * self.settings.deadendness_coeff
        # Remove a penalty for traveled edges
        heuristics += 1 - np.array([edge[2]['traveled'] or self.edge_sort(edge) in self.traveled_edges for edge in edges]) * self.settings.traveled_discount
        # Add a constant boost factor for finish nodes
        heuristics += np.array([end_node['is_finish_node'] for end_node in end_nodes]) * self.settings.finish_boost
        # TODO: Consider precomputing constant-to-end-node factors (deadendness, is_finish_node, etc) whenever settings are updated
        
        # Add other heuristics here

        pheromones = np.array([edge[2]['pheromone'] for edge in edges])

        desireabilities = pheromones**self.settings.pheromone_weight * \
            heuristics**self.settings.heuristic_weight
        return desireabilities