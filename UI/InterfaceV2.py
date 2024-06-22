import tkinter as tk
import networkx as nx
from PIL import Image, ImageTk
import pandas as pd
import os
import customtkinter as ctk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Graph.shortestpath import dijkstra
from unidecode import unidecode
from matplotlib import pyplot as plt
import mplcursors

class MetroAppUIV2(tk.Frame):
    def __init__(self, master=None, metro_graph=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App - V2")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        self.metro_graph = metro_graph
        self.selected_station_arrive_id = None
        self.selected_station_depart_id = None

        # Set the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        # Create the main window elements
        self.create_main_layout()

    ''' UI UTILITARY FUNCTIONS -- functions useful in the UI interface '''

    def display_graph(self):
        # Create a dictionary of positions using the 'pos' attribute of the nodes
        pos = {node: data['coordinates'] for node, data in self.metro_graph.nodes(data=True)}

        # Create a list of node ids in the same order as they are drawn on the matplotlib plot
        node_ids = list(self.metro_graph.nodes)

        # Create a matplotlib figure with specified size
        fig, ax = plt.subplots(figsize=(40, 20))  # Adjust the size here

        # Draw only the nodes on the figure with smaller size, using the positions from the 'pos' dictionary
        nodes = nx.draw_networkx_nodes(self.metro_graph, pos=pos, ax=ax, node_size=20)  # Adjust node_size as needed

        # Create a FigureCanvasTkAgg object and attach it to the canvas_frame
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Use mplcursors to add interactivity
        crs = mplcursors.cursor(nodes, hover=True)

        def on_add(sel):
            node_id = node_ids[sel.target.index]
            if node_id in self.metro_graph:
                node_data = self.metro_graph.nodes[node_id]
                print(node_data)  # Print the entire node data
                sel.annotation.set_text(node_data['name'])

        crs.connect("add", on_add)  # Connect the on_add function to the cursor

    def get_station_id_from_name(self, station_name):
        for node in self.metro_graph.nodes(data=True):
            if node[1]['name'] == station_name:
                return node[0]
        return None  # Return None if station name not found

    def create_quit_button(self):
        self.quit = ctk.CTkButton(self.control_frame, text="Quit the app", fg_color="red", command=self.master.destroy, hover_color="crimson")
        self.quit.pack(side="bottom", pady=10)

    ''' UI MANDATORY FUNCTIONS -- functions that do big things in UI '''

    def create_main_layout(self):
        # Create a frame for the controls
        self.control_frame = ctk.CTkFrame(self.master)
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Create the canvas for the image
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        # Display the graph
        self.display_graph()

        self.create_quit_button()
        self.create_input_controls()

    def on_src_entry_change(self, src_entry):
        # here we convert the input of user to lowercase in case he does maj
        user_input = unidecode(self.src_entry.get().strip().lower())

        # we start the search of station when we have 3 characters in the input
        if len(user_input) < 3:
            self.dropdown_menu_depart.pack_forget()
            return

        self.dropdown_menu_depart.delete(0, tk.END)
        matching_stations = []

        for node in self.metro_graph.nodes(data=True):
            station_name_normalized = unidecode(node[1]['name'].lower())
            if user_input in station_name_normalized:
                matching_stations.append(node[1]['name'])

        if matching_stations:
            for station in matching_stations:
                self.dropdown_menu_depart.insert(tk.END, station)
            self.dropdown_menu_depart.pack(anchor='w', pady=(5, 0), padx=(10, 10))
        else:
            self.dropdown_menu_depart.pack_forget()

        # Call on_dropdown_select with is_it_station_depart=True
        self.dropdown_menu_depart.bind("<<ListboxSelect>>", lambda event: self.on_dropdown_select(True, event))

    def on_des_entry_change(self, des_entry):
        user_input = unidecode(self.des_entry.get().strip().lower())

        # we start the search of station when we have 3 characters in the input
        if len(user_input) < 3:
            self.dropdown_menu_arrive.pack_forget()
            return
        self.dropdown_menu_arrive.delete(0, tk.END)
        matching_stations = []

        for node in self.metro_graph.nodes(data=True):
            station_name_normalized = unidecode(node[1]['name'].lower())
            if user_input in station_name_normalized:
                matching_stations.append(node[1]['name'])

        if matching_stations:
            for station in matching_stations:
                self.dropdown_menu_arrive.insert(tk.END, station)
            self.dropdown_menu_arrive.pack(anchor='w', pady=(5, 0), padx=(10, 10))
        else:
            self.dropdown_menu_arrive.pack_forget()

        self.dropdown_menu_arrive.bind("<<ListboxSelect>>", lambda event: self.on_dropdown_select(False, event))

    def on_dropdown_select(self, is_it_station_depart, event=None):
        if is_it_station_depart:
            if self.dropdown_menu_depart.curselection():
                selected_station = self.dropdown_menu_depart.get(self.dropdown_menu_depart.curselection()[0])
                self.src_entry.delete(0, tk.END)
                self.src_entry.insert(0, selected_station)
                self.selected_station_depart_id = self.get_station_id_from_name(selected_station)
                self.result_label.configure(text="Selected station: " + selected_station)
            self.dropdown_menu_depart.pack_forget()
        else:
            if self.dropdown_menu_arrive.curselection():
                selected_station = self.dropdown_menu_arrive.get(self.dropdown_menu_arrive.curselection()[0])
                self.des_entry.delete(0, tk.END)
                self.des_entry.insert(0, selected_station)
                self.selected_station_arrive_id = self.get_station_id_from_name(selected_station)
                self.result_label2.configure(text="Selected station: " + selected_station)
            self.dropdown_menu_arrive.pack_forget()

    def create_input_controls(self):
        # Configure appearance
        ctk.set_appearance_mode("automatic")
        ctk.set_default_color_theme("blue")

        # Depart
        src_label = ctk.CTkLabel(self.control_frame, text="Position de départ:", font=("Arial", 16))
        src_label.pack(anchor='w', pady=(30, 10), padx=(10, 10))
        # this deals with the entry of input of station de départ
        self.src_entry = ctk.CTkEntry(self.control_frame, font=("Arial", 16), width=300, height=40)
        self.src_entry.pack(anchor='w', pady=15, padx=(10, 10))
        self.src_entry.bind("<KeyRelease>", lambda event: self.on_src_entry_change(self.src_entry))

        # Label to display matching stations
        self.result_label = tk.Label(self.control_frame, text="", font=("Arial", 16))
        self.result_label.pack(anchor='w', pady=(5, 0), padx=(10, 10))

        # Dropdown menu for matching stations
        self.dropdown_menu_depart = tk.Listbox(self.control_frame, font=("Arial", 16), width=30, height=5)
        self.dropdown_menu_depart.bind("<<ListboxSelect>>", self.on_dropdown_select)

        # Destination
        des_label = ctk.CTkLabel(self.control_frame, text="Destination:", font=("Arial", 16))
        des_label.pack(anchor='w', pady=10, padx=(10, 10))
        # this deals with the entry of input of station de départ
        self.des_entry = ctk.CTkEntry(self.control_frame, font=("Arial", 16), width=300, height=40)
        self.des_entry.pack(anchor='w', pady=15, padx=(10, 10))
        self.des_entry.bind("<KeyRelease>", lambda event: self.on_des_entry_change(self.des_entry))

        # Label to display matching stations
        self.result_label2 = tk.Label(self.control_frame, text="", font=("Arial", 16))
        self.result_label2.pack(anchor='w', pady=5, padx=(10, 10))

        # Dropdown menu for matching stations
        self.dropdown_menu_arrive = tk.Listbox(self.control_frame, font=("Arial", 16), width=30, height=5)
        self.dropdown_menu_arrive.bind("<<ListboxSelect>>", self.on_dropdown_select)

        # Calculate button
        calc_button = ctk.CTkButton(
            self.control_frame,
            text="Calculer l'itinéraire",
            command=self.calculate_itinerary,
            text_color="white",
            font=("Arial", 20),
            fg_color="#669AEF",  # Button background color
            hover_color="#2563EB",  # Button color when hovered
            corner_radius=10,
            border_width=2,  # Border width
            border_color="#1D4ED8",  # Border color
            width=250,  # Adjusted width
            height=50  # Adjusted height
        )
        calc_button.pack(anchor='w', pady=10, padx=(10, 10))

    def calculate_itinerary(self):
        shortest_path = dijkstra(self.metro_graph, self.selected_station_depart_id, self.selected_station_arrive_id)
        print("The shortest path is:")
        print(shortest_path[0])
        print("The duration of the shortest path is:")
        print(shortest_path[1] // 60, "minutes", shortest_path[1] % 60, "secondes")