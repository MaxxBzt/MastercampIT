import tkinter as tk
import networkx as nx
from PIL import Image, ImageTk, ImageDraw
import pandas as pd
import os
import customtkinter as ctk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Data.ExtractData import dataversion1, merge_stations

from Graph.checkgraph import findACPM_Prim
from Graph.shortestpath import dijkstra
from unidecode import unidecode
from calc import carbon_saved
import mplcursors


class MetroAppUIV2(tk.Frame):
    def __init__(self, master=None, metro_graph=None, metro_line_image=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro, Efrei, Dodo")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.metro_graph = metro_graph

        self.metro_line_image = metro_line_image

        # Initialization of class variable
        self.image_original = None
        self.calc_button = None
        self.control_frame = None
        self.go_back_button = None
        self.itinerary_frame = None
        self.src_entry = None
        self.scrollable_frame = None
        self.selected_station_arrive_id = None
        self.selected_station_depart_id = None
        self.selecting_departure = True  # Indicator for which station the user is selecting

        # dictionary that will remember which point is linked to which coordinates
        self.coord_dict = {}

        # Set the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        # Create the main window elements
        self.create_main_layout()

        self.points_data = self.load_points()

    ''' UI UTILITARY FUNCTIONS -- functions useful in the UI interface '''

    def display_graph(self):
        # Create a dictionary of positions using the 'pos' attribute of the nodes
        pos = {node: data['coordinates'] for node, data in self.metro_graph.nodes(data=True)}

        # Create a list of node ids in the same order as they are drawn on the matplotlib plot
        node_ids = list(self.metro_graph.nodes)

        # Create a matplotlib figure with specified size
        fig, ax = plt.subplots(figsize=(20, 10))  # Adjust the size here

        # Set the background color to black
        ax.set_facecolor('#1A1A1A')

        # Adjust the subplot parameters to reduce the white border
        fig.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)

        # Draw only the nodes on the figure with smaller size, using the positions from the 'pos' dictionary
        # Set the node color to white
        nodes = nx.draw_networkx_nodes(self.metro_graph, pos=pos, ax=ax, node_size=20, node_color='white')



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
                sel.annotation.get_bbox_patch().set_facecolor('grey')  # Change the color here
                sel.annotation.get_bbox_patch().set_alpha(1.0)  # Make the background fully opaque
                sel.annotation.arrow_patch.set_color('red')

        crs.connect("add", on_add)  # Connect the on_add function to the cursor

    def display_graph_path(self, path):

        undirected_graph = self.metro_graph.to_undirected()

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Create a dictionary of positions using the 'pos' attribute of the nodes
        pos = {node: data['coordinates'] for node, data in undirected_graph.nodes(data=True)}

        # Create a list of node ids in the same order as they are drawn on the matplotlib plot
        node_ids = list(undirected_graph.nodes)

        # Create a matplotlib figure with specified size
        fig, ax = plt.subplots(figsize=(20, 10))  # Adjust the size here

        # Set the background color to black
        ax.set_facecolor('#1A1A1A')

        # Adjust the subplot parameters to reduce the white border
        fig.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)

        # Draw only the nodes on the figure with smaller size, using the positions from the 'pos' dictionary
        # Set the node color to white
        nodes = nx.draw_networkx_nodes(undirected_graph, pos=pos, ax=ax, node_size=20, node_color='white')


        # Create a FigureCanvasTkAgg object and attach it to the canvas_frame
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Use mplcursors to add interactivity
        crs = mplcursors.cursor(nodes, hover=True)

        if path is not None:
            # Extract only the station IDs from the path
            station_ids = [station_id for station_id, _, _ in path]
            # Create a list of tuples representing the edges in the path
            edges_in_path = [(station_ids[i], station_ids[i + 1]) for i in range(len(station_ids) - 1)]
            nx.draw_networkx_edges(undirected_graph, pos=pos, ax=ax, edgelist=edges_in_path, edge_color='yellow',
                                   width=2)

            # Get the names of the departure and destination stations
            depart_station_name = undirected_graph.nodes[station_ids[0]]['name']
            destination_station_name = undirected_graph.nodes[station_ids[-1]]['name']

            # Offset for the labels
            offset = 0.01

            # Create a dictionary with the positions of the departure and destination stations, adjusted by the offset
            labels_pos = {station_ids[0]: (pos[station_ids[0]][0], pos[station_ids[0]][1] + offset),
                          station_ids[-1]: (pos[station_ids[-1]][0], pos[station_ids[-1]][1] + offset)}

            # Create a dictionary with the names of the departure and destination stations
            labels = {station_ids[0]: depart_station_name, station_ids[-1]: destination_station_name}

            # Draw the labels with black text on a white background
            nx.draw_networkx_labels(undirected_graph, pos=labels_pos, labels=labels, font_color='black',
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'), ax=ax)
        def on_add(sel):
            node_id = node_ids[sel.target.index]
            if node_id in self.metro_graph:
                node_data = self.metro_graph.nodes[node_id]
                print(node_data)  # Print the entire node data
                sel.annotation.set_text(node_data['name'])
                sel.annotation.get_bbox_patch().set_facecolor('grey')  # Change the color here
                sel.annotation.get_bbox_patch().set_alpha(1.0)  # Make the background fully opaque
                sel.annotation.arrow_patch.set_color('red')

        crs.connect("add", on_add)  # Connect the on_add function to the cursor



    def find_station_id(self, event):
        # Get the id of the clicked object
        point_id = event.widget.find_closest(event.x, event.y)[0]
        if point_id in self.coord_dict:
            x, y, station_name = self.coord_dict[point_id]
            print(f"Coordonnées du point cliquées: ({x}, {y}, {station_name})")

            # Insert the station name into the appropriate entry field
            if self.selecting_departure:
                self.src_entry.delete(0, tk.END)
                self.src_entry.insert(0, station_name)
                self.selected_station_depart_id = self.get_station_id_from_name(station_name)
                self.src_entry.configure(border_color="green", border_width=2)
                self.check_entries()
            else:
                self.des_entry.delete(0, tk.END)
                self.des_entry.insert(0, station_name)
                self.selected_station_arrive_id = self.get_station_id_from_name(station_name)
                self.des_entry.configure(border_color="green", border_width=2)
                self.check_entries()
        else:
            print("Vous avez cliqué sur un point inconnu.")

        # this update the calculate itinerary button to make it disabled or not when necessary
        self.update_calc_button_state()

        # data=True get us : (node, node_attribute_dict)
        #        node = the node ID & node_attribute_dict a dictionary of the node's attributes
        # without it, we only get the node's ID, not attributes
        for node in self.metro_graph.nodes(data=True):
            if node[1]['name'] == station_name:
                print("Station ID:", node[0])
                break
        else:
            print("La station ", station_name, "n'a pas été trouvée.")

    def set_selecting_departure(self):
        self.selecting_departure = True

    def set_selecting_arrival(self):
        self.selecting_departure = False

    def get_station_id_from_name(self, station_name, line=None):
        for node in self.metro_graph.nodes(data=True):
            if node[1]['name'] == station_name and (line is None or node[1]['ligne'] == line):
                return node[0]
        return None  # Return None if station name not found

    ''' UI CREATE BUTTONS FUNCTIONS '''

    def create_go_back_button(self, frame):
        self.go_back_button = ctk.CTkButton(frame, text="Retour", width=250, height=50,
                                            fg_color="blue", command=self.go_back, hover_color="navy")
        self.go_back_button.pack(side="bottom", pady=10)

    ''' UI MANDATORY FUNCTIONS -- functions that do big things in UI '''


    def create_main_layout(self):
        # Create a frame for the controls
        self.control_frame = ctk.CTkFrame(self.master)
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Create the canvas for the image
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, background=self.master.cget('bg'), bd=0, highlightthickness=0,
                                relief='ridge')

        # Display the graph
        self.display_graph()

        # Buttons
        self.calc_button = None
        self.create_input_controls()
        # this update the calculate itinerary button to make it disabled or not when necessary
        self.update_calc_button_state()

    def update_calc_button_state(self):
        print(
            f"Departure station ID: {self.selected_station_depart_id}, Arrival station ID: {self.selected_station_arrive_id}")  # Debugging print statement
        if self.selected_station_depart_id is not None and self.selected_station_arrive_id is not None:
            self.calc_button.configure(state="normal")
        else:
            self.calc_button.configure(state="disabled")

    def on_enter(self, event):
        # Change the color of the point to indicate that it is being hovered over
        self.canvas.itemconfig(self.canvas.find_withtag("current"), fill='cyan')

    def on_leave(self, event):
        # Change the color of the point back to its original color
        self.canvas.itemconfig(self.canvas.find_withtag("current"), fill='white')

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

        self.check_entries()
    def check_entries(self):
        if self.src_entry.get() or self.des_entry.get():
            self.switch_button.configure(state="normal", border_color="black", border_width=2)


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

        self.check_entries()

    def on_dropdown_select(self, is_it_station_depart, event=None):
        if is_it_station_depart:
            if self.dropdown_menu_depart.curselection():
                selected_station = self.dropdown_menu_depart.get(self.dropdown_menu_depart.curselection()[0])
                self.src_entry.configure(border_color="green", border_width=2)
                self.src_entry.delete(0, tk.END)
                self.src_entry.insert(0, selected_station)
                self.selected_station_depart_id = self.get_station_id_from_name(selected_station)
                print(f"Departure station ID: {self.selected_station_depart_id}")  # Debugging print statement
            self.dropdown_menu_depart.pack_forget()
        else:
            if self.dropdown_menu_arrive.curselection():
                selected_station = self.dropdown_menu_arrive.get(self.dropdown_menu_arrive.curselection()[0])
                self.src_entry.configure(border_color="green", border_width=2)
                self.des_entry.delete(0, tk.END)
                self.des_entry.insert(0, selected_station)
                self.selected_station_arrive_id = self.get_station_id_from_name(selected_station)
                print(f"Arrival station ID: {self.selected_station_arrive_id}")  # Debugging print statement
            self.dropdown_menu_arrive.pack_forget()

        # this update the calculate itinerary button to make it disabled or not when necessary
        self.update_calc_button_state()

    def create_input_controls(self):
        # Configure appearance
        ctk.set_appearance_mode("automatic")
        ctk.set_default_color_theme("blue")
        # Depart
        src_label = ctk.CTkLabel(self.control_frame, text="Départ:", font=("Arial", 16))
        src_label.pack(anchor='w', pady=(30, 1), padx=(10, 10))
        # this deals with the entry of input of station de départ
        self.src_entry = ctk.CTkEntry(self.control_frame, font=("Arial", 16), width=300, height=40, border_color="grey",
                                      border_width=1)
        self.src_entry.pack(anchor='w', pady=5, padx=(10, 10))
        self.src_entry.bind("<KeyRelease>", lambda event: self.on_src_entry_change(self.src_entry))
        self.src_entry.bind("<FocusIn>", lambda event: self.set_selecting_departure())

        # Dropdown menu for matching stations
        self.dropdown_menu_depart = tk.Listbox(self.control_frame, font=("Arial", 16), width=30, height=5)
        self.dropdown_menu_depart.bind("<<ListboxSelect>>", self.on_dropdown_select)

        icon_switch = ctk.CTkImage(light_image=Image.open("assets/swap.png"),
                            size=(20, 20))

        self.switch_button = ctk.CTkButton(
            self.control_frame,
            command=lambda: self.switch_departure_arrival(),
            text= None,
            image=icon_switch,
            compound="left",
            font=("Arial", 13),
            fg_color="white",
            width=40,
            state="disabled",
            height=15,
        )
        self.switch_button.pack(anchor='w', pady=(10, 0), padx=(10, 10))  # Show the button

        des_label = ctk.CTkLabel(self.control_frame, text="Destination:", font=("Arial", 16))
        des_label.pack(anchor='w', pady=(10, 1), padx=(10, 10))
        # this deals with the entry of input of station de départ
        self.des_entry = ctk.CTkEntry(self.control_frame, font=("Arial", 16), width=300, height=40, border_color="grey",
                                      border_width=1)
        self.des_entry.pack(anchor='w', pady=5, padx=(10, 10))
        self.des_entry.bind("<KeyRelease>", lambda event: self.on_des_entry_change(self.des_entry))
        self.des_entry.bind("<FocusIn>", lambda event: self.set_selecting_arrival())
        icon = ctk.CTkImage(light_image=Image.open("Version1/LOGO_EFREI-WEB_blanc.png"),
                            size=(30, 30))

        set_station_button = ctk.CTkButton(
            self.control_frame,
            text="EFREI",
            command=lambda: self.set_station_as_destination('Villejuif, Louis Aragon'),
            text_color="white",
            image=icon,
            compound="left",
            font=("Arial", 13),
            fg_color="#163767",  # Button background color
            hover_color="#4396e2",  # Button color when hovered
            corner_radius=10,  # Rounded corners
            border_width=2,  # Border width
            border_color="#377fbc",  # Border color
            width=80,  # Adjusted width
            height=25  # Adjusted height
        )
        set_station_button.pack(anchor='w', pady=10, padx=(10, 10))

        # Dropdown menu for matching stations
        self.dropdown_menu_arrive = tk.Listbox(self.control_frame, font=("Arial", 16), width=30, height=5)
        self.dropdown_menu_arrive.bind("<<ListboxSelect>>", self.on_dropdown_select)

        button_frame = ctk.CTkFrame(self.control_frame)
        button_frame.pack(anchor='w', pady=10, padx=(10, 10))

        acpm_button = ctk.CTkButton(
            button_frame,
            text="Voir l'ACPM",
            command=self.show_acpm_tree,
            text_color="white",
            fg_color="#000000",
            hover_color="#4e4e4e",
            corner_radius=5,
            border_width=1,
            border_color="#4e4e4e",
            width = 120,
            height = 30
        )
        acpm_button.pack(side='left', padx=(0, 5))

        clear_button = ctk.CTkButton(
            button_frame,
            text="Réinitialiser l'itinéraire",
            command=self.clear_travel,
            text_color="#FFFFFF",
            font=("Arial", 14),
            fg_color="#FF4500",
            hover_color="#FF6347",
            corner_radius=5,
            border_width=1,
            border_color="#FF4500",
            width=120,
            height=30
        )
        clear_button.pack(side='left', padx=(5, 0))

        # Calculate button
        self.calc_button = ctk.CTkButton(
            self.control_frame,
            text="Calculer l'itinéraire",
            command=self.calculate_itinerary,
            text_color="white",
            font=("Arial", 20),
            fg_color="#669AEF",  # Button background color
            hover_color="#2563EB",  # Button color when hovered
            corner_radius=10,  # Rounded corners
            width=280,  # Adjusted width
            height=50,  # Adjusted height
            state="disabled"
        )
        self.calc_button.pack(anchor='w', pady=10, padx=(10, 10))

    def set_station_as_destination(self, station_name):
        """Set a specific station as the destination."""
        self.des_entry.delete(0, tk.END)
        self.des_entry.insert(0, station_name)
        self.selected_station_arrive_id = self.get_station_id_from_name(station_name)
        self.des_entry.configure(border_color="green", border_width=2)

        # this update the calculate itinerary button to make it disabled or not when necessary
        self.update_calc_button_state()

    def show_acpm_tree(self):
        ACPM = findACPM_Prim(self.metro_graph)
        print("The total weight of the ACPM is:")
        print(ACPM.size(weight='duration'))

        # Create a dictionary mapping node IDs to station names
        labels = {node[0]: node[1]['name'] for node in ACPM.nodes(data=True)}

        pos = {}

        # Iterate through nodes in ACPM
        for node in ACPM.nodes(data=True):
            node_id = node[0]
            station_name = node[1]['name']

            # Find coordinates for this station name in coord_dict
            for key, value in self.coord_dict.items():
                if value[2] == station_name:
                    # Adjust coordinates if necessary to correct orientation
                    pos[node_id] = (value[0], value[1])  # Set pos[node_id] to (x, y) coordinates
                    break  # Stop searching once found

        # Display ACPM in new window thanks to plt
        plt.figure(figsize=(10, 10))  # Adjust figure size as needed
        nx.draw_networkx(ACPM, pos=pos, with_labels=True, labels=labels, node_size=100, node_color='skyblue',
                         edge_color='black')

        # Adjust plot limits if necessary
        plt.xlim(min(x for x, y in pos.values()) - 50, max(x for x, y in pos.values()) + 50)
        plt.ylim(min(y for x, y in pos.values()) - 50, max(y for x, y in pos.values()) + 50)

        plt.gca().invert_yaxis()  # Invert y-axis if needed

        plt.show()

    ''' UI --- CALCULTE ITINERARY '''

    def create_itinerary_layout(self):

        # Create a frame for the itinerary controls
        self.itinerary_frame = ctk.CTkFrame(self.master)
        self.itinerary_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Pack the "Quit the app" button into the itinerary frame
        self.create_go_back_button(self.itinerary_frame)

    def create_metro_line_button(self, station_id, station_name, is_it_depart, station_nbr):
        station_nbr = self.metro_graph.nodes[station_id]['ligne']
        line_image_path, line_color = (self.metro_line_image[station_nbr][0],
                                       self.metro_line_image[station_nbr][1])
        line_image = ctk.CTkImage(light_image=Image.open(line_image_path), size=(30, 30))

        if is_it_depart:
            fg_color = "black"

        else:
            fg_color = "#163767"
        # Create station change button
        station_change_button = ctk.CTkButton(
            self.scrollable_frame,
            text=station_name,
            text_color="white",
            image=line_image,
            compound="left",
            font=("Arial", 20),
            fg_color=fg_color,
            corner_radius=10,
            border_width=2,
            border_color=fg_color,
            width=10,
            hover=False,
            height=10
        )
        station_change_button.pack(anchor='center', pady=10, padx=(10, 10))

        return line_color

    def create_station_button(self, station_name, next_is_line_change):

        if next_is_line_change == "True":
            button_text = f"Change line station at {station_name}"
            button_color = "#7f7f7f"
            button = ctk.CTkButton(
                self.scrollable_frame,
                text=button_text,
                hover=False,
                fg_color=button_color
            )

        elif next_is_line_change == "Endstation":
            button_text = "You've arrived at destination."
            button_color = "green"
            button = ctk.CTkButton(
                self.scrollable_frame,
                text=button_text,
                hover=False,
                fg_color=button_color
            )
        else:
            button = ctk.CTkButton(
                self.scrollable_frame,
                text=station_name,
                hover=False,
            )
        button.pack(pady=2, anchor='center')

    def get_station_coordinates(self, station_name):
        for point_id, (x, y, name) in self.coord_dict.items():
            if name == station_name:
                return x, y
        return None

    def get_line_color(self, station_id):
        station_nbr = self.metro_graph.nodes[station_id]['ligne']
        return self.metro_line_image.get(station_nbr, ("", ""))[1]

    def display_metro_line_images(self, total_weight, path):
        # Remove existing itinerary widgets from itinerary frame
        for widget in self.itinerary_frame.winfo_children():
            if not isinstance(widget, ctk.CTkButton):  # Skip destroying the back button
                widget.destroy()

        self.total_weight_label = None

        # Convert total weight to hours and minutes
        hours = total_weight // 3600
        minutes = (total_weight % 3600) // 60

        clockicon = ctk.CTkImage(light_image=Image.open("assets/clock.png"), size=(15, 15))

        # Display total weight in hours and minutes only if hours > 0
        if hours > 0:
            total_weight_label = ctk.CTkLabel(self.itinerary_frame,
                                              text=f"Temps de trajet: {hours} hours {minutes} minutes",
                                              wraplength=200, image=clockicon, compound="left", padx=5, width=150,
                                              height=30, font=("Arial", 15))
            total_weight_label.pack(pady=10)
        else:
            total_weight_label = ctk.CTkLabel(self.itinerary_frame, text=f"Temps de trajet: {minutes} minutes",
                                              wraplength=200, image=clockicon, compound="left", padx=5, width=150,
                                              height=30, font=("Arial", 15))
            total_weight_label.pack(pady=10)

            # Create a green label with icon to display CO2 saved
            leaficon = ctk.CTkImage(light_image=Image.open("assets/feuille.png"), size=(15, 15))
            text_CO2 = f"CO2 saved: {carbon_saved(total_weight)} g"

            # Check the current appearance mode and adjust the background color
            if ctk.get_appearance_mode() == "Dark":
                bg_color = "#456442"  # Darker shade of green
            else:
                bg_color = "#67ef79"  # Original green color

            co2_label = ctk.CTkLabel(self.itinerary_frame, text=text_CO2, wraplength=200, font=("Arial", 15),
                                     bg_color=bg_color, image=leaficon, compound="left", padx=5, width=150, height=30)
            co2_label.pack(pady=5)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.itinerary_frame, width=400, height=200)

        self.scrollable_frame.pack(side="left", fill="y", padx=20, pady=20)

        for i, (station_id, line_change, station_nbr) in enumerate(path):
            station_name = self.metro_graph.nodes[station_id]['name']

            next_station_is_line_change = "False"
            # if we are the station de depart
            if station_id == path[0][0] or station_id == path[len(path) - 1][0]:

                line_color = self.create_metro_line_button(station_id, station_name, True, station_nbr)
            else:
                if not line_change:
                    # if not a line change but the next station is a line change and has the same station name
                    if i + 1 < len(path):
                        next_station_id, next_line_change, _ = path[i + 1]
                        next_station_name = self.metro_graph.nodes[next_station_id]['name']
                        if next_line_change and next_station_name == station_name:
                            next_station_is_line_change = "True"
                            if next_station_name == self.metro_graph.nodes[self.selected_station_arrive_id]['name']:
                                next_station_is_line_change = "Endstation"
                    self.create_station_button(station_name, next_station_is_line_change)

                # Check if there's a metro line change (True) to display the metro line image
                if line_change:
                    line_color = self.create_metro_line_button(station_id, station_name, False, station_nbr)


    def calculate_itinerary(self):
        print("Calculating itinerary...")

        # Hide the main layout
        self.control_frame.pack_forget()

        # Call the new layout
        self.create_itinerary_layout()

        # calculate the shortest path
        path, total_weight = dijkstra(self.metro_graph, self.selected_station_depart_id,
                                      self.selected_station_arrive_id)

        print("Shortest path:", path)
        # display the path on the graph
        self.display_graph_path(path)
        # Display metro line images with station names and buttons
        self.display_metro_line_images(total_weight, path)





    def go_back(self):
        # Hide itinerary details
        self.itinerary_frame.pack_forget()
        self.clear_travel()

        # Show the original controls
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        self.des_entry.delete(0, tk.END)
        self.src_entry.delete(0, tk.END)

        # Remove current "Go Back" and "Quit the app" buttons (if they exist)
        if hasattr(self, 'go_back_button'):
            self.go_back_button.pack_forget()


    def clear_travel(self):
        self.selected_station_depart_id = None
        self.selected_station_arrive_id = None
        self.selecting_departure = True

        # Clear src_entry and des_entry
        self.src_entry.delete(0, tk.END)
        self.des_entry.delete(0, tk.END)

        self.src_entry.configure(border_color="grey", border_width=1)
        self.des_entry.configure(border_color="grey", border_width=1)

        # Clear dropdown menus and hide them
        self.dropdown_menu_depart.delete(0, tk.END)
        self.dropdown_menu_depart.pack_forget()
        self.dropdown_menu_arrive.delete(0, tk.END)
        self.dropdown_menu_arrive.pack_forget()

        self.update_calc_button_state()

        self.switch_button.configure(state="disabled", border_color="white")

    def switch_departure_arrival(self):


        # Swap selected station IDs
        self.selected_station_depart_id, self.selected_station_arrive_id = (
            self.selected_station_arrive_id, self.selected_station_depart_id)

        # Swap entry field contents
        src_text = self.src_entry.get()
        des_text = self.des_entry.get()






        self.src_entry.delete(0, tk.END)
        self.src_entry.insert(0, des_text)
        self.des_entry.delete(0, tk.END)
        self.des_entry.insert(0, src_text)

        if self.des_entry.get():
            self.des_entry.configure(border_color="green", border_width=2)
        else:
            self.des_entry.configure(border_color="grey", border_width=1)

        if self.src_entry.get():
            self.src_entry.configure(border_color="green", border_width=2)
        else:
            self.src_entry.configure(border_color="grey", border_width=1)