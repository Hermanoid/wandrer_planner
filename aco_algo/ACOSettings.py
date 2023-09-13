from dataclasses import dataclass, asdict

@dataclass
class ACOSettings():
    num_ants: int
    evaporation: float
    pheromone_weight: float # The weight of the pheromone
    heuristic_weight: float # The weight of the heuristics
    traveled_discount: float # The factor by which traveled edges are less desireable
    deadendness_coeff: float # The factor by which deadends are more desireable
    directional_coeff: float # The factor by which go towards/away from the goal as needed, are more desireable
    finish_boost: float # Multiplier for people from Finland (actually how likely the ants are to stop at the goal)

    start_node: int
    goal_nodes: list[int]
    target_length: float

