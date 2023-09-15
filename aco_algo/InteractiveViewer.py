from matplotlib import pyplot as plt
import matplotlib.cm as mplcm
import numpy as np
import networkx as nx
import osmnx as ox
from PIL import Image, ImageTk
import tkinter as tk

from .ACOSettings import ACOSettings
from .Ant import Ant, RunResult
from .AntColony import AntColony


class InteractiveViewer:
    def __init__(self, colony: AntColony):
        self.colony = colony
        self.graph = colony.network_graph
        # self.fig = plt.figure()
        # self.ax = self.fig.add_subplot(111)
        # self.ax.set_title('ACO Algorithm')
        self.pher_cmap = mplcm.get_cmap("viridis")
        self.route_cmap = mplcm.get_cmap("rainbow")

        self.window = tk.Tk()
        self.window.rowconfigure(0, minsize=800, weight=1)
        self.window.columnconfigure(0, minsize=800, weight=1)
        self.window.columnconfigure(1, minsize=200, weight=1)

        # convert to tkinter compatible image
        self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(np.zeros((800,800,3), dtype=np.uint8)))
        # put the image on a label
        self.image_label = tk.Label(self.window, image=self.imgtk)
        self.image_label.image = self.imgtk # Prevent garbage collection

        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.frm_controls = tk.Frame(self.window, relief="raised", bd=2)
        self.frm_controls.grid(row=0, column=1, sticky="nsew")

        # Buttons for reset, pause/play, and step
        self.btn_reset = tk.Button(self.frm_controls, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.playing = False
        self.btn_toggle = tk.Button(self.frm_controls, text="Play", command=self.toggle)
        self.btn_toggle.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.btn_step = tk.Button(self.frm_controls, text="Step", command=self.step)
        self.btn_step.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Set up app exit stuff
        self.window.bind('<Escape>', lambda e: self.window.quit())

    def reset(self):
        self.colony.reset()
        self.show_frame()

    def toggle(self):
        self.playing = not self.playing
        if self.playing:
            self.btn_toggle.configure(text="Pause")
            self.run_iteration()
        else:
            self.btn_toggle.configure(text="Play")

    def step(self):
        # Ignore steps if we're already playing as fast as we can.
        if not self.playing:
            self.run_iteration()

    def run_iteration(self):
        results = self.colony.run_iteration()
        self.show_frame(results)
        # Repeat the same process after every 10 seconds
        if self.playing:
            self.image_label.after(10, self.run_iteration)

    def show_frame(self, results: list[RunResult] | None =None):
        pheromones = np.array(list(nx.get_edge_attributes(self.graph, "pheromone").values()))
        params = {
            "node_size": 0,
            "edge_color": self.pher_cmap(pheromones),
            "bgcolor": "black",
            "show": False,
        }
        if results:
            routes = [result.route for result in results]
            route_colors = [self.route_cmap(i/len(routes)) for i in range(len(routes))]
            # To HTML (to avoid some error warnings)
            route_colors = [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" for r,g,b,_ in route_colors]
            fig, ax = ox.plot_graph_routes(self.graph, routes, **params, route_colors=route_colors)
        else:
            fig, ax = ox.plot_graph(self.graph, **params)
        fig.canvas.draw()

        # convert canvas to image
        im = Image.frombytes('RGB', fig.canvas.get_width_height(),fig.canvas.tostring_rgb())
        
        # Convert captured image to photoimage
        self.imgtk = ImageTk.PhotoImage(image=im)
    
        # Displaying photoimage in the label
        self.image_label.image = self.imgtk # Prevent garbage collection
        # Configure image in the label
        self.image_label.configure(image=self.imgtk)

    def run(self):
        self.window.after(10, self.run_iteration)
        self.window.mainloop()