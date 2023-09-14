import networkx as nx
from .ACOSettings import ACOSettings
import numpy as np
import itertools

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
        while current_node not in self.finish_nodes:
            outgoing_edges = list(self.network_graph.edges(current_node, data=True))

            if(len(self.route) <= 2):
                # If we're just starting out, don't allow our poor ant to immediately finish
                outgoing_edges = list(filter(lambda edge: edge[1] not in self.finish_nodes, outgoing_edges))

            if len(outgoing_edges) == 1:
                # If we go down a dead end, the only way out is back the way we came!
                # We can skip the desireability calculation in this case.
                chosen_edge = outgoing_edges[0]
            else:
                desireabilities = self.desireabilities(outgoing_edges)
                desireabilities = desireabilities / np.sum(desireabilities)
                chosen_ind = np.random.choice(len(outgoing_edges), 1, p=desireabilities)
                chosen_edge = outgoing_edges[chosen_ind[0]]

            current_node = chosen_edge[1]
            self.route.append(current_node)
            self.traveled_edges.add(self.edge_sort(chosen_edge))
            self.traveled_length += chosen_edge[2]['length']

        return self.route, self.traveled_length

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
        gohome = self.settings.gohome_boost > 0 and self.traveled_length > self.settings.target_length
        if self.settings.directional_coeff > 0 or gohome:
            # Calculate dist diffs (see function comment)
            dist_diffs = np.array([self.calc_dist_diff(edge) for edge in edges])
            # if gohome:
            #     # Add a quadratically-increasing boost for going home
            #     # As distance increases beyond the target, this should quickly cause the ant to follow the shortest path to a goal.
            #     heuristics += (dist_diffs-np.max(dist_diffs))**2 * self.settings.gohome_boost
            if self.settings.directional_coeff > 0:
                # Normalize diffs for relative comparison
                dist_diffs_norm = (dist_diffs - np.mean(dist_diffs)) / np.std(dist_diffs)
                # Smack it with a sigmoid (https://eelslap.com/)
                # Leave out the negative sign because we want this to be a decreasing function (more diff = less desireable)
                dist_diffs_sig = 1 / (1 + np.exp(dist_diffs_norm * self.settings.directional_choosiness))
                # Finally, scale and add to heuristics
                heuristics += dist_diffs_sig * self.settings.directional_coeff

        # The lads that have traveled
        traveled_lads = np.array([edge[2]['traveled'] or self.edge_sort(edge) in self.traveled_edges for edge in edges])
        # Add a boost for deadend-ier nodes (except for traveled deadends)
        heuristics += np.array([end_node['deadendness'] for end_node in end_nodes]) * self.settings.deadendness_coeff * traveled_lads
        # Add a constant boost factor for finish nodes
        heuristics += np.array([end_node['is_finish_node'] for end_node in end_nodes]) * self.settings.finish_boost
        # TODO: Consider precomputing these factors that are constant to given node, traveled status, and settings 
        # (deadendness, is_finish_node, etc) 
        
        # Add other heuristics here

        pheromones = np.array([edge[2]['pheromone'] for edge in edges])

        desireabilities = pheromones**self.settings.pheromone_weight * \
            heuristics**self.settings.heuristic_weight * \
            (1 - traveled_lads * self.settings.traveled_discount)
        return desireabilities