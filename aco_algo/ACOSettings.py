from dataclasses import dataclass, asdict

@dataclass
class ACOSettings():
    num_ants: int
    evaporation: float
    pheromone_weight: float # The weight of the pheromone
    heuristic_weight: float # The weight of the heuristics
    traveled_factor: float # The factor by which traveled edges are less desireable
    deadendness_factor: float # The factor by which deadends are more desireable
    directional_factor: float # The factor by which go towards/away from the goal as needed, are more desireable

    start_node: int
    goal_nodes: list[int]
    target_length: float

