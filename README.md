# Wandrer Planner
### An optimal path finder for the [Wandrer.earth](wandrer.earth) run-every-road game.

This project is a small passion project for a road-biker who thought, "there's no way somebody hasn't built this yet." Be the change you want to see in the world, eh?

I did contact Wandrer's legendary Craig about this feature and it sounds like an official version of this tool is already under construction. Keep your eyes peeled for that.

---

Overview of this project:

It's under construction, nothing fancy yet. I've attempted an AStar-based algorithmic solution. Results: I was smart enough to make it work, but not quite smart enough to realize that I was creating a naive solution to what is basically a form of the Traveling Salesman Problem. The complexity was basically exponential over distance when I ran it in a city-block setting, where prospective paths split 3 ways (left, right, or center) every ~110 meters (the length of a city block). That's no fun!

The next solution I'm attempting is based on Ant Colony Optimization, using techniques laid out [here](https://staff.washington.edu/paymana/swarm/stutzle99-eaecs.pdf) and some other fun sources.

If and when I've found an acceptable solution, I plan to add a UI so users can see the generated path and tune some parameters (target length, etc), add an export to Strava function, and bundle it into a mostly-portable executable.

---

### Brief-ish explanation of the algorithm
The fancy bit of this system is the graph optimization search (or optimi**s**ation search, since I'm in NZ at the time of writing). This centers around the Exploration Graph.

The Exploration Graph does behave like a classic implicit graph search in that it progressively searches through the state space, and it employs A* heuristics. However, for the exploration graph, a path through the world (the "network graph", a networkx MultiDiGraph loaded from Wandrer data) is a node, and we don't keep track of the path-of-paths (the sequence of arc-addings that built up the path). Each Exploration Path has an associated score, and heuristics are based on the whole Path. The goal of this graph search is to find an Exploration Path which optimizes this score.

As you might imagine, the design of this score defines what kind of result this search produces. This score is "indexed" off the scores that Wandrer gives, so each new kilometer traveled (that was previously untraveled) is one point, with penalties given for stuff like going over the target distance or traveling outside the target region. (Minor note - the algorithm actually uses meters). There are settings for how these penalties are scaled - the intention is that it will be possible to change these settings interactively to get the perfect path for a scenario. The highest possible score would be exactly equal to the target distance. In this case, a path would have been found with a length exactly equal to the target length (i.e. it did not go over-distance or under-distance at all) and only passes through untraveled edges. 

To help this search kick out paths that are definitely sub-optimal, this search employs a heuristic. Just like A*, a each prospective path is given an f-score which is the sum of the score the path has achieved so far, plus a heuristic of how well a path could do in a best-case scenario. Lets say the target length is 10 kilometers and a path has already covered 7 beautiful, untouched, untraveled kilometers - in the opposite direction of the goal. Lets say the goal was 4 kilometers from the start. In this case, in the best case, the path would have to travel `7 + 4 = 11` kilometers (through more untraveled roads, since this is an ideal case) to the goal. The f-score of this path would take into effect `7 + 11 = 18` kilometers of new terrain (good!), but 8 kilometers of "overlength" distance (bad). The user might think this is great and willingly take on the extra distance. In this case, they could set the overlength penalty to slightly more than 1, so the untraveled roads and overlength distance almost cancel out. They can't completely cancel out because if they did, the algorithm would find a route that covers basically every available untraveled road. Usually, however, this extra distance will need to be penalized with a overlength penalty factor of substantially more than 1 - lets say 2. The f-score would thus be `18 - 8 * 2 = 2` - not so good. The algorithm should probably spend its time searching a different route.

This graph is optimizing a path that ends in the goal, not just a path *to* the goal. This means that the optimal path might pass through the goal node, do a loop, and then return to the goal. Because of this, when a path is found that reaches a goal location, it is not immediately returned, but added to a max heap (separate from the one that drives the search frontier) of found route possibilities. The search continues until no unexplored search path has a better best-case f-score than the best of the found routes. 

Check out [algo_test](astar_algo/algo_test.ipynb) for a view of this stuff in action. 