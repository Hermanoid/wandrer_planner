from collections import namedtuple
from networkx import MultiDiGraph
import pyproj


class ExplorationGraphSettings():
    def __init__(self, target_length: float, overlength_penalty: float, outregion_penalty: float, start_nodes: list[int], goal_nodes: list[int]):
        self.target_length = target_length
        self.overlength_penalty = overlength_penalty
        self.outregion_penalty = outregion_penalty
        self.start_nodes = start_nodes
        self.goal_nodes = goal_nodes
    
# class ExplorationNode():
#     def __init__(self, node: str, traveled: bool, length: float):
#         self.node = node
#         self.traveled = traveled
#         self.length = length

class ExplorationArc(namedtuple("ExplorationArc", ["tail", "head", "key", "attributes"])):
    pass

class ExplorationPath():
    def __init__(self, arcs: list[ExplorationArc], total_length: float, new_length: float, score: float, node_pairs: set[tuple[int, int]] | None = None):
        self.arcs = arcs
        self.total_length = total_length
        self.new_length = new_length
        self.score = score
        self.node_pairs = node_pairs or set((arc.tail, arc.head) for arc in arcs)

    def has_traveled_arc(self, arc: ExplorationArc):
        return (arc.tail, arc.head) in self.node_pairs or (arc.head, arc.tail) in self.node_pairs
    
class ExplorationGraph():
    """This is a concrete subclass of Graph where vertices and edges
     are explicitly enumerated. Objects of this type are useful for
     testing graph algorithms."""

    def __init__(self, network_graph: MultiDiGraph, settings: ExplorationGraphSettings, crs="WSG84"):
        """Initialises an explicit graph.
        Keyword arguments:
        network_graph - a MultiDiGraph of the network we're exploring. Must include length and traveled edge attributes.
        """

        assert all(network_graph.has_node(n) for n in settings.start_nodes), "Start node must be in graph"
        assert all(network_graph.has_node(n) for n in settings.goal_nodes), "Goal node must be in graph"
        assert settings.target_length > 0, "Target length must be positive"

        self.network_graph = network_graph
        self.settings = settings
        self._goal_locs = [network_graph.nodes[g] for g in settings.goal_nodes]
        # self._start_nodes = [settings.start]
        self.geod = pyproj.Geod(ellps=crs)


    def distance(self, node1, node2):
        """Returns the distance between two nodes"""
        return self.geod.inv(node1['x'], node1['y'], node2['x'], node2['y'])[2]

    def best_case_score(self, path: ExplorationPath):
        """Return the estimated (best-case) score to a goal node from the given node.
        This method is required for informed search.
        The "best-case" situation assumes that whatever has happened with this pass so far,
        from now on it is able to take new, untraveled roads directly away from/towards the goal as needed.
        """

        head_loc = self.network_graph.nodes[path.arcs[-1].head]
        dist_to_goal = min(self.distance(head_loc, goal_loc) for goal_loc in self._goal_locs)
        target_length = self.settings.target_length

        scored_dist = max(target_length - path.total_length, 0)
        overlength_dist = max(dist_to_goal - scored_dist, 0)
        return path.score + scored_dist - overlength_dist * self.settings.overlength_penalty

    def starting_nodes(self):
        """Returns a sequence of starting nodes."""
        return self.settings.start_nodes

    def reached_goal(self, path):
        """Returns true if the given node is a goal node."""
        return path.arcs[-1].head in self.settings.goal_nodes

    def outgoing_arcs(self, node):
        """Returns a sequence of Arc objects that go out from the given
        node. The action string is automatically generated.

        """
        arcs = [ExplorationArc(*edge) for edge in self.network_graph.edges(node, data=True, keys=True)]
        return arcs

    def continuing_paths(self, path: ExplorationPath):
        """Given a path, return a sequence of paths that continue from it.
        """

        arcs = self.outgoing_arcs(path.arcs[-1].head)
        return [ExplorationPath(
                path.arcs + [arc], 
                path.total_length + arc.attributes['length'],
                path.new_length if arc.attributes["traveled"] else path.new_length + arc.attributes['length'],
                path.score + self.score_arc(path, arc),
                path.node_pairs | {(arc.tail, arc.head)}) 
            for arc in arcs]
    
    def score_arc(self, path: ExplorationPath, arc: ExplorationArc):
        """Calculate change in a path's score when adding a new arc"""
        # This math is similar to the heuristic, but not quite the same.
        # The heuristic does not clamp the scored distance (it is whatever is optimal)
        # This one clamps scored_dist to the arc's length and considers whether the arc has been traveled
        length_to_add = arc.attributes['length']
        target_length = self.settings.target_length

        remaining_dist = max(target_length - path.total_length, 0)
        scored_dist = min(length_to_add, remaining_dist)
        overlength_dist = max(length_to_add - remaining_dist, 0)
        overlength_penalty = - (overlength_dist * self.settings.overlength_penalty)

        traveled = arc.attributes["traveled"] or path.has_traveled_arc(arc)

        return overlength_penalty if traveled else scored_dist + overlength_penalty
