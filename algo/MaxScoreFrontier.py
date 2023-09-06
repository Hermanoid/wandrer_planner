from ExplorationGraph import ExplorationGraph, ExplorationPath
from MaxHeap import MaxHeap


class MaxScoreFrontier():
    """ Implements a frontier for a A*-like Great Score search.
        It's like LCFS + Hueristic, but we use the min heap with negated numbers to make it a max heap.
        Additionally, unlike a classic frontier, the nodes are paths through the network (road) graph 
            and we don't keep track of the path-of-paths.
            
        Pruning wouldn't do any good. The network graph has cycles, yes, 
        but each node in this graph represents a built-up path through that graph (so there can't be cycles)"""

    def __init__(self, graph: ExplorationGraph):
        """ Takes in an ExplorationGraph for calculating the heuristic"""
        self.heap = MaxHeap()
        self.graph = graph

    def add(self, path: ExplorationPath):
        heuristic = self.graph.best_case_score(path)
        self.heap.push(heuristic, path)
    
    def best_f_score(self):
        return self.heap.peek_score()
    
    def empty(self):
        return len(self.heap) == 0

    def __iter__(self):
        """The object returns itself because it is implementing a __next__
        method and does not need any additional state for iteration."""
        return self
        
    def __next__(self):
        if len(self.heap) > 0:
            return self.heap.pop()
        raise StopIteration   # don't change this one