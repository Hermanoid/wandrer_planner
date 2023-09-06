import heapq

class MaxHeap():
    """
    Minimal Implementation of a max heap using heapq
    It's basically just a heapq heap with negated scores to simulate a max heap
    """
    def __init__(self):
        self.container = []
        self.counter = 0

    def __len__(self):
        return len(self.container)
    
    def __str__(self):
        return str(self.container)
    
    def __repr__(self):
        return repr(self.container)
    
    def __iter__(self):
        return iter(self.container)

    def push(self, score: float, path):
        # The counter is used as a tiebreaker for nodes with the same score
        # (instead of the hash of the path, which might be expensive to get and unpredictable)
        heapq.heappush(self.container, (-score, self.counter, path))
        self.counter += 1

    def pop(self):
        return heapq.heappop(self.container)[-1]

    def peek(self):
        return self.container[0][-1]
    
    def peek_score(self):
        return -self.container[0][0]

    def empty(self):
        return len(self.container) == 0
        