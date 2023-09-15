import networkx as nx
import numpy as np
import multiprocessing

from .Ant import Ant, RunResult
from .ACOSettings import ACOSettings

def run_ant(ant):
    return ant.run()

class AntColony():
    def __init__(self, network_graph: nx.MultiGraph, initial_settings: ACOSettings):
        """
        Construct a new Ant Colony for holding the network graph and settings.
        Warning: the provided network graph is modified in place to include all sorts of attributes.
        """
        print("Ant Colony Algo Init")
        # Copy and unfreeze the input graph for modification
        self.network_graph = nx.MultiGraph(network_graph)

        print("Precomputing betweenness centrality")
        # Betweenness is used as a measure of how isolated a node is in the graph.
        # Isolated regions (like dead ends) tend to be overlooked by the algorithm
        #   because you generally have to travel them twice, in and out.
        # Deadendness is here to counteract that force and make sure you hit 
        #   dead ends the first time you go by them.
        k=min(1000, len(self.network_graph.nodes))
        self.betweenness_centrality = nx.betweenness_centrality(self.network_graph, weight='length', k=k)
        nx.set_node_attributes(self.network_graph, self.betweenness_centrality, 'betweenness_centrality')

        self.update_settings(initial_settings)

        print("Ant Colony Algo Init Done")

    def update_settings(self, new_settings: ACOSettings, initial=True):
        print("Updating Settings and doing some precomputation")
        reset_pheromones = initial
        deadendness = {node: 1/1000*betweenness for node, betweenness in self.betweenness_centrality.items()}
        nx.set_node_attributes(self.network_graph, deadendness, 'deadendness')

        # Add some fake nodes to the graph to represent "finishing" as an action
        # This way, each ant can decide whether to finish at a goal node or keep going.
        if initial or new_settings.goal_nodes != self.settings.goal_nodes:
            # Find the lengths of shortest paths from any goal to any node in the graph.
            # (Used as a more-accurate heuristic for the ant's goal-directedness)
            lengths = nx.multi_source_dijkstra_path_length(self.network_graph, new_settings.goal_nodes, weight='length')
            nx.set_node_attributes(self.network_graph, lengths, 'shortest_path_to_goal')
            
            # Deal with finish nodes
            self.setup_finish_nodes(new_settings, initial)
            # Changing finish nodes involves permuting the graph, so we need to reset pheromones
            reset_pheromones = True

        if initial or new_settings.num_ants != self.settings.num_ants:
            # Instantiate some ants!
            self.ants = [Ant(self.network_graph, new_settings) for _ in range(new_settings.num_ants)]

        if reset_pheromones:
            self.reset()
        self.settings = new_settings
        print("Settings updated")

    def setup_finish_nodes(self, new_settings, initial):
        if not initial:
            for finish_node in self.finish_nodes:
                self.network_graph.remove_node(finish_node)
        node_count = self.network_graph.number_of_nodes()
        self.finish_nodes = set()
        for goal_node in new_settings.goal_nodes:
            self.network_graph.add_node(node_count, **self.network_graph.nodes[goal_node])
            self.network_graph.add_edge(goal_node, node_count, length=0, traveled=False)
            self.finish_nodes.add(node_count)
            node_count += 1
        self.network_graph.graph["finish_nodes"] = self.finish_nodes
        nx.set_node_attributes(self.network_graph, {node: (node in self.finish_nodes) for node in self.network_graph.nodes}, 'is_finish_node')

    def reset(self):
        nx.set_edge_attributes(self.network_graph, 1, 'pheromone')

    def run_pool(self):
        # Run all the ants in parallel
        # Ah, the joys of sidestepping the GIL... 
        # our dandy graph will be copied to each process, but I'm sure we'll have plenty of memory
        with multiprocessing.Pool() as pool:
            results = pool.map(Ant.run, self.ants)
        # TODO: As usual with parallelism, I need to see if this even helps!
        return results
    
    def run_sequential(self):
        results = [ant.run() for ant in self.ants]
        return results

    def score(self, route_result: RunResult):
        """Every good optimisation algorithm needs a good objective function."""
        # The simplest objective is pure new length
        # I'll add deadend, regions, etc later.
        return route_result.newly_traveled_length

    def run_iteration(self):
        results = self.run_sequential()
        scores = [self.score(result) for result in results]

        # Evaporation!
        for edge in self.network_graph.edges:
            self.network_graph.edges[edge]['pheromone'] *= (1-self.settings.evaporation)
        
        # Insert elitism here... for now, just apply a simple pheromone update
        for result, score in zip(results, scores):
            for edge in result.traveled_edges:
                self.network_graph.edges[edge]['pheromone'] += score

        return results
