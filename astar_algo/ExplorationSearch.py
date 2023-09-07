from .ExplorationGraph import ExplorationArc, ExplorationGraph, ExplorationGraphSettings, ExplorationPath
from .MaxHeap import MaxHeap
from .MaxScoreFrontier import MaxScoreFrontier
import networkx as nx

def optimal_path_search_internal(graph: ExplorationGraph, frontier: MaxScoreFrontier):
    """
    Implements a spicy version of A* search.
    The key unique bit is that, when a goal is found, we don't stop.
    Instead, we keep going until we've explored all paths that could be better (according to the heuristics)
      than the best path found so far.

    """

    found_paths = MaxHeap()

    for starting_node in graph.starting_nodes():
        # Add some single-arc dummy paths to the frontier to start the search
        frontier.add(ExplorationPath([ExplorationArc(None, starting_node, 0, None),], 0, 0, 0))
    
    for path in frontier:
        if graph.reached_goal(path):
            found_paths.push(path.score, path)

        for cpath in graph.continuing_paths(path):
            frontier.add(cpath) # add a new extended path

        if frontier.empty() or (not found_paths.empty() and frontier.best_f_score() < found_paths.peek_score()):
            # If the best available path (best-case) is worse than the best found path, we're done
            # (unless the user wants to keep generating less-optimal paths)
            # We need to check this after expanding the current path, because the best path might be a continuation of the current path
            yield found_paths.pop()

def optimal_path_search(graph: nx.MultiDiGraph, settings: ExplorationGraphSettings, crs="WGS84"):
    ex_graph = ExplorationGraph(graph, settings, crs=crs)
    frontier = MaxScoreFrontier(ex_graph)
    return optimal_path_search_internal(ex_graph, frontier)