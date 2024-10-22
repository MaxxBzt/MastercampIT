import datetime
import tkinter as tk
import networkx as nx
from PIL import Image, ImageTk, ImageDraw
from Data.utilities import metro_lines_info
import pandas as pd
import os
import customtkinter as ctk
import matplotlib

import UI.theme as theme

matplotlib.use('TkAgg')

#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Data.ExtractData import dataversion1, merge_stations

from Graph.checkgraph import findACPM_Prim
from Graph.shortestpath import dijkstra
from unidecode import unidecode
from calc import carbon_saved
import mplcursors
import darkdetect


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
        self.shop_frame = None
        self.map_frame = None
        self.go_back_button = None
        self.itinerary_frame = None
        self.src_entry = None
        self.selected_search_id = None
        self.scrollable_frame = None
        self.selected_station_arrive_id = None
        self.selected_station_depart_id = None
        self.selecting_departure = True  # Indicator for which station the user is selecting
        self.current_frame = None
        self.is_selecting_search = False


        # dictionary that will remember which point is linked to which coordinates
        self.coord_dict = {}

        self.master.configure(fg_color=theme.theme_background)

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
        fig, ax = plt.subplots(figsize=(20, 10))  # Adjust the size here

        # Set the background color to black
        # Check if user is in dark mode
        if darkdetect.isDark():
            ax.set_facecolor(theme.theme_background[1])
        else:
            ax.set_facecolor(theme.theme_background[0])

        # Adjust the subplot parameters to reduce the white border
        fig.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)

        # Draw only the nodes on the figure with smaller size, using the positions from the 'pos' dictionary
        # Set the node color to white
        if darkdetect.isDark():
            nodes = nx.draw_networkx_nodes(self.metro_graph, pos=pos, ax=ax, node_size=20, node_color='white')
        else:
            nodes = nx.draw_networkx_nodes(self.metro_graph, pos=pos, ax=ax, node_size=20, node_color='black')

        if darkdetect.isDark():
            fig.set_facecolor(theme.theme_background[1])
        else:
            fig.set_facecolor(theme.theme_background[0])
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
                #print(node_data)  # Print the entire node data
                sel.annotation.set_text(node_data['name'])
                # Change text color
                sel.annotation.set_color('white')
                sel.annotation.get_bbox_patch().set_facecolor('grey')  # Change the color here
                sel.annotation.get_bbox_patch().set_alpha(1.0)  # Make the background fully opaque
                sel.annotation.arrow_patch.set_color('red')

        crs.connect("add", on_add)  # Connect the on_add function to the cursor


    def get_points(self):
        with open("Data/coins.txt", "r") as file:
            # opens file and counts number of entries
            coins = file.readlines()
            print("Number of coins: ", len(coins))
            return len(coins)

    def addpoint(self):
        # check if there is no more than two points in the day :
        with open("Data/coins.txt", "r") as file:
            # if there are two or more points today, do nothing
            points = file.readlines()
            count = 0
            for point in points:
                if str(datetime.datetime.now().date()) in point:
                    count += 1
                    if count >= 2:
                        return
        with open("Data/coins.txt", "a") as file:
            # write the date and hour in the file
            file.write("Date: " + str(datetime.datetime.now()) + "\n")

        # add a point to the user
        self.pointscounter.configure(text=str(self.get_points()))

    def remove_point(self,number):
        # Take all the points
        with open("Data/coins.txt", "r") as file:
            points = file.readlines()
        # Remove the last number of points
        with open("Data/coins.txt", "w") as file:
            file.writelines(points[:-number])
        # Update the points counter
        self.pointscounter.configure(text=str(self.get_points()))

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
        if darkdetect.isDark():
            ax.set_facecolor(theme.theme_background[1])
        else:
            ax.set_facecolor(theme.theme_background[0])

        # Adjust the subplot parameters to reduce the white border
        fig.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.07)

        # Draw only the nodes on the figure with smaller size, using the positions from the 'pos' dictionary
        # Set the node color to white
        if darkdetect.isDark():
            nodes = nx.draw_networkx_nodes(undirected_graph, pos=pos, ax=ax, node_size=20, node_color='white')
        else:
            nodes = nx.draw_networkx_nodes(undirected_graph, pos=pos, ax=ax, node_size=20, node_color='black')

        if darkdetect.isDark():
            fig.set_facecolor(theme.theme_background[1])
        else:
            fig.set_facecolor(theme.theme_background[0])

        # Create a FigureCanvasTkAgg object and attach it to the canvas_frame
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Use mplcursors to add interactivity
        crs = mplcursors.cursor(nodes, hover=True)

        if path is not None:
            # Extract only the station IDs from the path
            station_ids = [station_id for station_id, _, _ in path]
            # Create a list of edges
            edges_in_path = [(station_ids[i], station_ids[i + 1]) for i in range(len(station_ids) - 1)]

            # Create a list of colors for each edge based on the line to which the station belongs
            edge_colors = [metro_lines_info[self.metro_graph.nodes[station_ids[i]]['ligne']][1] for i in
                           range(len(station_ids) - 1)]

            # Draw the edges with the corresponding colors
            nx.draw_networkx_edges(undirected_graph, pos=pos, ax=ax, edgelist=edges_in_path, edge_color=edge_colors,
                                   width=2)



        def on_add(sel):
            node_id = node_ids[sel.target.index]
            if node_id in self.metro_graph:
                node_data = self.metro_graph.nodes[node_id]
                #print(node_data)  # Print the entire node data
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
            #print(f"Coordonnées du point cliquées: ({x}, {y}, {station_name})")

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
                #print("Station ID:", node[0])
                break
        else:
            print("La station ", station_name, "n'a pas été trouvée.")

    def set_selecting_departure(self):
        self.selecting_departure = True

    def set_selecting_search(self):
        self.is_selecting_search = True

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
                                            fg_color=theme.theme_menu, text_color="white", command=self.go_back, hover_color=theme.theme_hover)
        self.go_back_button.pack(side="bottom", pady=10)

    ''' UI MANDATORY FUNCTIONS -- functions that do big things in UI '''

    def display_map_tab(self):

        if self.current_frame != self.map_frame:
            self.current_frame.pack_forget()
            self.canvas_frame.pack_forget()
            # Call the new layout
            self.create_map_layout()



    def display_home_tab(self):
        if self.current_frame != self.control_frame:
            # Hide the main layout
            self.current_frame.pack_forget()
            self.canvas_frame.pack_forget()
            # Show the original controls
            self.control_frame.pack(side="left", fill="y", padx=20, pady=20)
            self.current_frame = self.control_frame
            self.canvas_frame.pack(side="right", fill="both", expand=True)
            self.clear_travel()

            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            self.display_graph()

    def nav_bar(self):
        self.nav_frame = ctk.CTkFrame(self.master, fg_color=theme.theme_background)
        self.nav_frame.pack(side="top", fill="x")

        self.home_button = ctk.CTkButton(self.nav_frame, text="Accueil", fg_color=theme.theme_menu, hover=False,
                                         command=lambda: self.display_home_tab())
        self.home_button.pack(side="left", padx=(20, 10), pady=(10, 10))

        self.map_button = ctk.CTkButton(self.nav_frame, text="Détails de la carte", hover=False,
                                        fg_color=theme.theme_menu,
                                        command=lambda: self.display_map_tab())
        self.map_button.pack(side="left", padx=(10, 0), pady=(10, 10))

        self.shop_button = ctk.CTkButton(self.nav_frame, text="Boutique", fg_color=theme.theme_menu, hover=False,
                                         command=lambda: self.create_shop_layout())
        self.shop_button.pack(side="left", padx=(10, 0), pady=(10, 10))

    def create_main_layout(self):

        self.nav_bar()
        # Create a frame for the controls
        self.control_frame = ctk.CTkFrame(self.master, fg_color=theme.theme_frame)
        self.current_frame = self.control_frame
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Create the canvas for the image
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, background="#323232", bd=0, highlightthickness=0,
                                relief='ridge')

        # Points counter placed at the top right

        # Load the coin image

        # Frame of the points counter with adjusted size and padding
        self.coinframe = ctk.CTkFrame(
            self.master,
            width=100,  # Adjust width to accommodate the border and content
            height=80,  # Adjust height to accommodate the border and content
            border_width=10,
            border_color="#ffd635",
            fg_color="transparent"
        )
        self.coinframe.place(relx=1.0, y=10, anchor='ne', x=-20)

        # Load the coin image
        self.coin_image = Image.open("assets/star.png")
        self.coin_photo = ctk.CTkImage(light_image=self.coin_image, size=(35, 35))

        # Create the points counter label
        self.pointscounter = ctk.CTkLabel(
            self.coinframe,
            text=str(self.get_points()),
            image=self.coin_photo,
            font=("Arial", 30),
            compound="right"
        )
        self.pointscounter.pack(padx=5, pady=5)  # Add padding inside the coinframe

        # Display the graph
        self.display_graph()

        # Buttons
        self.calc_button = None
        self.create_input_controls()
        # this update the calculate itinerary button to make it disabled or not when necessary
        self.update_calc_button_state()

    def update_calc_button_state(self):
        #print(
            #f"Departure station ID: {self.selected_station_depart_id}, Arrival station ID: {self.selected_station_arrive_id}")  # Debugging print statement
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
                matching_stations.append(node[1]['name'] + " - Ligne " + str(node[1]['ligne']))

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
                matching_stations.append(node[1]['name'] + " - Ligne " + str(node[1]['ligne']))

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
                station = selected_station.split(" - Ligne ")[0].strip()
                line = selected_station.split(" - Ligne ")[1].strip()
                self.src_entry.configure(border_color="green", border_width=2)
                self.src_entry.delete(0, tk.END)
                self.src_entry.insert(0, selected_station)
                self.selected_station_depart_id = self.get_station_id_from_name(station, str(line))
            self.dropdown_menu_depart.pack_forget()
        elif not is_it_station_depart:

            if self.dropdown_menu_arrive.curselection():
                selected_station = self.dropdown_menu_arrive.get(self.dropdown_menu_arrive.curselection()[0])
                station = selected_station.split(" - Ligne ")[0]
                line = selected_station.split(" - Ligne ")[1]
                self.des_entry.configure(border_color="green", border_width=2)
                self.des_entry.delete(0, tk.END)
                self.des_entry.insert(0, selected_station)
                self.selected_station_arrive_id = self.get_station_id_from_name(station, str(line))
            self.dropdown_menu_arrive.pack_forget()

        if is_it_station_depart == None:
            if self.dropdown_search.curselection():
                selected_station = self.dropdown_search.get(self.dropdown_search.curselection()[0])
                self.search_entry.configure(border_color="green", border_width=2)
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, selected_station)
                self.display_stations(selected_station)
            self.dropdown_search.pack_forget()

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
            command=lambda: self.set_station_as_destination('Villejuif - Louis Aragon'),
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

        button_frame = ctk.CTkFrame(self.control_frame, fg_color=theme.theme_frame)
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
            text_color="white",
            font=("Arial", 14),
            fg_color="#eb5149",
            hover_color="#ec7e7a",
            corner_radius=5,
            border_width=1,
            border_color="#ec7e7a",
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
            fg_color=theme.theme_menu,  # Button background color
            hover_color=theme.theme_hover,  # Button color when hovered
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
        self.selected_station_arrive_id = "IDFM:463269"
        self.des_entry.configure(border_color="green", border_width=2)

        # this update the calculate itinerary button to make it disabled or not when necessary
        self.update_calc_button_state()

    def show_acpm_tree(self):
        ACPM = findACPM_Prim(self.metro_graph)
        print("The total weight of the ACPM is:")
        print(ACPM.size(weight='duration'))

        # Create a dictionary mapping node IDs to station names
        labels = {node[0]: node[1]['name'] for node in ACPM.nodes(data=True)}

        #pos = {}

        # Iterate through nodes in ACPM
        for node in ACPM.nodes(data=True):
            node_id = node[0]
            station_name = node[1]['name']

        plt.close('all')
        # Display ACPM in new window thanks to plt
        plt.figure(figsize=(10, 10))  # Adjust figure size as needed
        nx.draw_networkx(ACPM, with_labels=False, labels=labels, node_size=100, node_color='skyblue',
                         edge_color='black')
        plt.show()


        #plt.show()

    ''' UI --- CALCULTE ITINERARY '''

    def create_itinerary_layout(self):

        # Create a frame for the itinerary controls
        self.itinerary_frame = ctk.CTkFrame(self.master, fg_color=theme.theme_frame)
        self.current_frame = self.itinerary_frame
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

        # Load the wheelchair icon if applicable
        wheelchair_icon = None
        if self.metro_graph.nodes[station_id].get('wheelchair') == '1':
            wheelchair_icon = ctk.CTkImage(light_image=Image.open("assets/disabled.png"), size=(20, 20))
            # Create a frame to hold the icon and the button
            frame = ctk.CTkFrame(self.scrollable_frame, fg_color='transparent')
            frame.pack(anchor='center', pady=10, padx=(10, 10), fill='x')

        if wheelchair_icon:

            # Create a label for the wheelchair icon
            icon_label = ctk.CTkLabel(frame, image=wheelchair_icon, text="")
            icon_label.pack(side='left', padx=(0, 5))

            station_change_button = ctk.CTkButton(
                frame,
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
                height=10,
            )

        else:
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

    def create_station_button(self, station_name, next_is_line_change, station_id):

        # Load the wheelchair icon if applicable
        wheelchair_icon = None
        if self.metro_graph.nodes[station_id].get('wheelchair') == '1':
            wheelchair_icon = ctk.CTkImage(light_image=Image.open("assets/disabled.png"), size=(20, 20))
            # Create a frame to hold the icon and the button
            frame = ctk.CTkFrame(self.scrollable_frame, fg_color='transparent')

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
            if wheelchair_icon:
                frame.pack(anchor='center', pady=10, padx=(10, 10), fill='x')
                # Create a label for the wheelchair icon
                button = ctk.CTkButton(
                    frame,
                    text=station_name,
                    image=wheelchair_icon,
                    hover=False,
                    fg_color=theme.theme_stations,
                    text_color="white",
                )
            else:
                button = ctk.CTkButton(
                    self.scrollable_frame,
                    text=station_name,
                    hover=False,
                    fg_color=theme.theme_stations,
                    text_color="white",
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
                bg_color = "#D3FFD3"  # Original green color

            co2_label = ctk.CTkLabel(self.itinerary_frame, text=text_CO2, wraplength=200, font=("Arial", 15),
                                     bg_color=bg_color, image=leaficon, compound="left", padx=5, width=150, height=30)
            co2_label.pack(pady=5)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.itinerary_frame, width=400, height=200, fg_color=theme.theme_frame)

        self.scrollable_frame.pack(side="left", fill="y", padx=20, pady=20)

        for i, (station_id, line_change, station_nbr) in enumerate(path):
            station_name = self.metro_graph.nodes[station_id]['name']

            next_station_is_line_change = "False"
            # if we are the station de depart
            if station_id == path[0][0] or station_id == path[len(path) - 1][0]:

                self.create_metro_line_button(station_id, station_name, True, station_nbr)


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
                    self.create_station_button(station_name, next_station_is_line_change, station_id)

                # Check if there's a metro line change (True) to display the metro line image
                if line_change:
                    self.create_metro_line_button(station_id, station_name, False, station_nbr)


    def calculate_itinerary(self):
        #print("Calculating itinerary...")

        # Hide the main layout
        self.control_frame.pack_forget()
        self.canvas_frame.pack_forget()

        # Call the new layout
        self.create_itinerary_layout()

        # Re-pack the canvas frame to fit alongside the itinerary frame
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        # calculate the shortest path
        path, total_weight = dijkstra(self.metro_graph, self.selected_station_depart_id,
                                      self.selected_station_arrive_id)

        #print("Shortest path:", path)

        # Display the path on the graph
        self.display_graph_path(path)


        # Display metro line images with station names and buttons
        self.display_metro_line_images(total_weight, path)





    def go_back(self):
        # Hide itinerary details
        self.itinerary_frame.pack_forget()
        self.canvas_frame.pack_forget()
        self.clear_travel()

        # Show the original controls
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        self.des_entry.delete(0, tk.END)
        self.src_entry.delete(0, tk.END)

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()


        self.display_graph()

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

    ''' UI --- MAP  LAYOUT'''

    def create_map_layout(self):

        # Create a frame for the itinerary controls
        self.map_frame = ctk.CTkFrame(self.master, fg_color=theme.theme_frame)
        self.current_frame = self.map_frame
        self.map_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.canvas_frame.pack(side="right", fill="both", expand=True)
        self.display_search_entry_on_map()

    def display_search_entry_on_map(self):

        search_label = ctk.CTkLabel(self.map_frame, text="Search for a station:", font=("Arial", 16))
        search_label.pack(anchor='w', pady=(30, 1), padx=(10, 10))
        # this deals with the entry of input of station de départ
        self.search_entry = ctk.CTkEntry(self.map_frame, font=("Arial", 16), width=300, height=40, border_color="grey",
                                         border_width=1)
        self.search_entry.pack(anchor='w', pady=5, padx=(10, 10))
        self.search_entry.bind("<KeyRelease>", lambda event: self.on_search_entry(self.search_entry))
        self.search_entry.bind("<FocusIn>", lambda event: self.set_selecting_search())

        scrollable_frame_on_map_frame = ctk.CTkScrollableFrame(self.map_frame, width=200, height=10,
                                                               fg_color=theme.theme_frame)
        scrollable_frame_on_map_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Dropdown menu for matching stations
        self.dropdown_search = tk.Listbox(self.map_frame, font=("Arial", 16), width=30, height=5)
        self.dropdown_search.bind("<<ListboxSelect>>", self.on_dropdown_select)

        for line_number, (image_path, color) in self.metro_line_image.items():
            line_image = ctk.CTkImage(light_image=Image.open(image_path),
                                      size=(30, 30))

            button = ctk.CTkButton(
                scrollable_frame_on_map_frame,
                text=f"Ligne {line_number}",
                text_color="white",
                image=line_image,
                compound="left",
                font=("Arial", 14),
                fg_color=color,
                corner_radius=10,
                border_width=2,
                border_color=color,
                width=10,
                hover=False,
                height=10
            )
            button.image = line_image  # Retain a reference to the image to prevent garbage collection
            button.pack(anchor='center', pady=10, padx=(10, 10))

            button.bind("<Button-1>", lambda event, line=line_number: self.display_stations_at_line(line))

    def display_stations(self, station_name):

        for widget in self.map_frame.winfo_children():
            if not isinstance(widget, ctk.CTkButton):
                widget.destroy()

        self.display_stations_frame = ctk.CTkFrame(self.map_frame, fg_color=theme.theme_frame)
        self.display_stations_frame.pack(side="left", fill="y", padx=20, pady=20)

        text_line = f"Corresponding lines for {station_name}"

        # Check the current appearance mode and adjust the background color
        if ctk.get_appearance_mode() == "Dark":
            bg_color = "#262525"  # Darker shade of green
            text_color = "white"
        else:
            bg_color = "#fffdfb"  # Original green color
            text_color = "black"

        line_label = ctk.CTkLabel(self.display_stations_frame, text=text_line, wraplength=200, font=("Arial", 15),
                                  bg_color=bg_color, text_color=text_color, compound="left", padx=5, width=250)
        line_label.pack(pady=5)

        self.scrollable_frame_map = ctk.CTkScrollableFrame(self.display_stations_frame, width=400, height=10,
                                                           fg_color=theme.theme_frame)
        self.scrollable_frame_map.pack(side="left", fill="y", padx=20, pady=20)

        lines = set()
        # Collect unique line numbers for the given station_name
        for node in self.metro_graph.nodes(data=True):
            if node[1]['name'] == station_name:
                lines.add(node[1]['ligne'])

        # Create a button for each unique line number
        for station_nbr in lines:
            line_image_path = self.metro_line_image[station_nbr][0]
            line_image = ctk.CTkImage(light_image=Image.open(line_image_path), size=(30, 30))

            # Get the background color for the button from metro_lines_info
            bg_color_button = self.metro_line_image[station_nbr][1]

            button = ctk.CTkButton(
                self.scrollable_frame_map,
                text=f"Ligne {station_nbr}",
                text_color="white",
                image=line_image,
                compound="left",
                font=("Arial", 20),
                fg_color=bg_color_button,
                corner_radius=10,
                border_width=2,
                border_color=bg_color_button,
                width=10,
                hover=False,
                height=10
            )
            button.pack(anchor='center', pady=10, padx=(10, 10))

        # Create the "Go Back" button
        self.create_back_button(self.scrollable_frame_map)

    def on_search_entry(self, search_entry):

        user_input = unidecode(self.search_entry.get().strip().lower())

        # we start the search of station when we have 3 characters in the input
        if len(user_input) < 3:
            self.dropdown_search.pack_forget()
            return

        self.dropdown_search.delete(0, tk.END)
        matching_stations = []

        for node in self.metro_graph.nodes(data=True):
            station_name_normalized = unidecode(node[1]['name'].lower())
            if user_input in station_name_normalized:
                matching_stations.append(node[1]['name'])

        if matching_stations:
            for station in matching_stations:
                self.dropdown_search.insert(tk.END, station)
            self.dropdown_search.pack(anchor='w', pady=(5, 0), padx=(10, 10))
        else:
            self.dropdown_search.pack_forget()

        # Call on_dropdown_select with is_it_station_depart=True
        self.dropdown_search.bind("<<ListboxSelect>>", lambda event: self.on_dropdown_select(None, event))

    def create_back_button(self, frame):
        self.go_back_button_map = ctk.CTkButton(frame, text="Retour", width=250, height=50,
                                                fg_color=theme.theme_menu, text_color="white", hover_color=theme.theme_hover,
                                                command=self.go_back_to_map)
        self.go_back_button_map.pack(side="bottom", pady=10)

    def go_back_to_map(self):

        self.scrollable_frame_map.pack_forget()
        self.display_stations_frame.pack_forget()

        # Show the original controls
        self.map_frame.pack(side="left", fill="y", padx=20, pady=20)

        if hasattr(self, 'go_back_button_map'):
            self.go_back_button_map.pack_forget()

        self.display_search_entry_on_map()

    def get_stations_for_line(self, line_number):

        stations = []
        for node in self.metro_graph.nodes(data=True):
            if 'ligne' in node[1] and node[1]['ligne'] == line_number:
                stations.append(node[1]['name'])

        return stations

    def display_stations_at_line(self, line_nbr):

        for widget in self.map_frame.winfo_children():
            if not isinstance(widget, ctk.CTkButton):
                widget.destroy()

        self.display_stations_at_line_frame = ctk.CTkFrame(self.map_frame, fg_color=theme.theme_frame)
        self.display_stations_at_line_frame.pack(side="left", fill="y", padx=20, pady=20)

        stations = self.get_stations_for_line(line_nbr)

        bg_color_button = self.metro_line_image[line_nbr][1]
        line_image_path = self.metro_line_image[line_nbr][0]
        line_image = ctk.CTkImage(light_image=Image.open(line_image_path), size=(30, 30))

        title_button = ctk.CTkButton(
            self.display_stations_at_line_frame,
            text=f"Ligne {line_nbr}",
            text_color="white",
            image=line_image,
            compound="left",
            font=("Arial", 20),
            fg_color=bg_color_button,
            corner_radius=10,
            border_width=2,
            border_color=bg_color_button,
            width=10,
            hover=False,
            height=10
        )
        title_button.pack(pady=2, anchor='center')

        self.scrollable_frame_display_stations_at_line_frame = ctk.CTkScrollableFrame(
            self.display_stations_at_line_frame,
            width=400, height=10, fg_color=theme.theme_frame)
        self.scrollable_frame_display_stations_at_line_frame.pack(side="left", fill="y", padx=20, pady=20)

        for station in stations:
            button = ctk.CTkButton(
                self.scrollable_frame_display_stations_at_line_frame,
                text=station,
                hover=False,
                fg_color=theme.theme_stations,
                text_color="white"
            )
            button.pack(pady=2, anchor='center')



    ''' UI --- SHOP '''

    def create_shop_layout(self):

        if self.current_frame != self.shop_frame:
            self.canvas_frame.pack_forget()
            self.current_frame.pack_forget()

            self.shop_frame = ctk.CTkFrame(self.master, fg_color=theme.theme_background)
            self.current_frame = self.shop_frame
            self.shop_frame.pack(fill="both", expand=True, padx=20, pady=20)
            shop_tabview = ctk.CTkTabview(self.shop_frame,
                                          width=600,
                                          height=250,
                                          corner_radius=10,
                                          fg_color=theme.theme_frame,
                                          segmented_button_fg_color="white",
                                          segmented_button_selected_color=theme.theme_hover,
                                          segmented_button_selected_hover_color=theme.theme_hover,
                                          segmented_button_unselected_hover_color=theme.theme_menu,
                                          segmented_button_unselected_color=theme.theme_tab,
                                          text_color="white",
                                          state="normal")
            shop_tabview.pack(fill="both", expand=True, padx=20, pady=20)

            shop_tabview.add("Thèmes")
            shop_tabview.add("Objets")
            shop_tabview.add("Argent")
            shop_tabview.add("Charité")
            shop_tabview.set("Thèmes")

            self.items_images = ["assets/shop/amazon.png", "assets/shop/backpack.png",
                            "assets/shop/theiere.png", "assets/shop/board_game.png"]
            items_titles = [
                "Carte cadeau Amazon",
                "Sac à dos de voyage",
                "Ensemble de théière en céramique",
                "Jeu de société pour toute la famille"
            ]
            items_descriptions = [
                "Offrez la liberté de choisir parmi des millions de produits avec une carte cadeau Amazon.",
                "Sac à dos durable et fonctionnel, idéal pour les voyages et les excursions.",
                "Ensemble élégant de théière et tasses en céramique, parfait pour les moments de détente.",
                "Jeu de société interactif qui promet des heures de plaisir en famille ou entre amis."
            ]
            items_prices = [150, 200, 130, 100]

            self.themes_images = ["assets/shop/theme_green.png", "assets/shop/theme_blue.png", "assets/shop/theme_pink.png",
                             "assets/shop/theme_yellow.png", "assets/shop/theme_purple.png"]
            themes_titles = ["Thème Vert", "Thème Bleu", "Thème Rose", "Thème Jaune", "Thème par Défaut"]
            themes_descriptions = ["Change le thème de l'application en vert",
                                   "Change le thème de l'application en bleu",
                                   "Change le thème de l'application en rose",
                                   "Change le thème de l'application en jaune",
                                   "Revient au thème par défaut de l'application : violet"]

            themes_prices = [5, 5, 5, 5, 5]

            self.money_images = ["assets/shop/coin.png", "assets/shop/coin.png", "assets/shop/billet_argent.png",
                            "assets/shop/billet_argent.png"]
            money_titles = [
                "Virement bancaire 5 euros",
                "Virement bancaire 15 euros",
                "Virement bancaire 50 euros",
                "Virement bancaire 100 euros"
            ]
            money_descriptions = [
                "Recevez un virement bancaire d'une valeur de 5 euros, utilisable librement.",
                "Recevez un virement bancaire d'une valeur de 15 euros, utilisable librement.",
                "Recevez un virement bancaire d'une valeur de 50 euros, utilisable librement.",
                "Recevez un virement bancaire d'une valeur de 100 euros, utilisable librement."
            ]
            money_prices = [300, 800, 1500, 3500]

            self.charity_images = ["assets/shop/croix_rouge.png", "assets/shop/secours_pop.png",
                              "assets/shop/greenpeace-logo.jpg",
                              "assets/shop/wwf.png"]
            charity_titles = [
                "Greenpeace",
                "WWW France",
                "Croix-Rouge française",
                "Secours Populaire Français",

            ]
            charity_descriptions = [
                "Association qui agissent selon les principes de non-violence pour protéger l’environnement, la biodiversité et promouvoir la paix. Elle s’appuie sur un mouvement de citoyennes.",
                "Association pour ârrêter la dégradation de l'environnement dans le monde et construire un avenir où les êtres humains pourront vivre en harmonie avec la nature.",
                "Association humanitaire française fondée en 1864, reconnue d'utilité publique. Elle agit sur le territoire français.",
                "Association à but non lucratif créée en 1945. Elle lutte contre la pauvreté et l'exclusion en France et dans le monde..",
            ]
            charity_prices = [50, 50, 50, 50]

            self.add_buttons_to_tab(shop_tabview.tab("Objets"), self.items_images, items_titles, items_descriptions,
                                    items_prices, self.buy_other,"item")
            self.add_buttons_to_tab(shop_tabview.tab("Thèmes"), self.themes_images, themes_titles, themes_descriptions,
                                    themes_prices, self.buy_other,"theme")
            self.add_buttons_to_tab(shop_tabview.tab("Argent"), self.money_images, money_titles, money_descriptions,
                                    money_prices, self.buy_other,"money")
            self.add_buttons_to_tab(shop_tabview.tab("Charité"), self.charity_images, charity_titles, charity_descriptions,
                                    charity_prices, self.buy_other,"charity")

    def add_buttons_to_tab(self, tab, images, titles, descriptions, prices, command,tab_category):
        num_buttons = len(images)
        themes_colors = [("#E7F8E7", "#2B5C2B"), ("#D8E8FF", "#1B2735"), ("#ffe7fa", "#5A2C47"), ("#feffe5", "#3F3B1D"),
                         ("#e6d6ff", "#323232")]
        for index in range(num_buttons):
            i, j = divmod(index, 3)  # Calculate row and column dynamically

            if tab_category == "theme":
                frame = ctk.CTkFrame(tab, fg_color=themes_colors[index])
            else:
                frame = ctk.CTkFrame(tab, fg_color=theme.theme_tab)

            # Load and display image
            image = ctk.CTkImage(light_image=Image.open(images[index]), size=(50, 50))
            image_label = ctk.CTkLabel(frame, image=image, text="")
            image_label.pack(padx=10, pady=10)

            # Title label
            title_label = ctk.CTkLabel(frame, text=titles[index], font=("Helvetica", 14, "bold"))
            title_label.pack(padx=10, pady=5)

            # Description label with wrapping
            if tab_category == "charity":
                description_label = ctk.CTkLabel(frame, text=descriptions[index], wraplength=200, font=("Helvetica", 9))
            else:
                description_label = ctk.CTkLabel(frame, text=descriptions[index], wraplength=200)
            description_label.pack(padx=10, pady=5)

            # Price label
            price_label = ctk.CTkLabel(frame, text=f"{prices[index]} Coins", font=("Helvetica", 12, "bold"))
            price_label.pack(padx=10, pady=5)

            # Buy button
            button_command = self.create_button_command(index, command, prices[index], tab_category)
            button = ctk.CTkButton(frame, text="Buy", fg_color=theme.theme_menu, hover_color="black",
                                   command=button_command)
            button.pack(padx=10, pady=10)

            # Pack the frame into the tab
            frame.grid(row=i, column=j, padx=20, pady=20, sticky="nsew")

            # Configure weights for tab
            tab.grid_rowconfigure(i, weight=1)
            tab.grid_columnconfigure(j, weight=1)

    def create_button_command(self, index, command, price, tab_category):
        def command_wrapper():
            total_indices = len(self.themes_images) + len(self.items_images) + len(self.money_images) + len(
                self.charity_images)
            if tab_category == "theme":
                adjusted_index = index
            elif tab_category == "item":
                adjusted_index = len(self.themes_images) + index
            elif tab_category == "money":
                adjusted_index = len(self.themes_images) + len(self.items_images) + index
            elif tab_category == "charity":
                adjusted_index = len(self.themes_images) + len(self.items_images) + len(self.money_images) + index
            else:
                adjusted_index = index  # Fallback to default index

            print(f"Clicked button with index: {adjusted_index}")
            command(adjusted_index, price)

        return command_wrapper

    def buy_other(self, index, item_price):
        if self.get_points() >= item_price:
            purchase_type = self.determine_purchase_type(index)
            if purchase_type == "item":
                self.remove_point(item_price)
                tk.messagebox.showinfo("Achat réussi",
                                       "Votre article vous sera envoyé sous peu à l'adresse indiquée sur votre compte.")

            elif purchase_type == "money":
                self.remove_point(item_price)
                tk.messagebox.showinfo("Achat réussi", "Vous recevrez un e-mail pour poursuivre le virement bancaire.")
            elif purchase_type == "theme":
                self.remove_point(item_price)
                self.process_theme_purchase(index)
            else:
                self.remove_point(item_price)
                tk.messagebox.showinfo("Achat réussi", "Merci pour votre don à une œuvre caritative.")

        else:
            # Inform the user of insufficient points or coins
            tk.messagebox.showerror("Points insuffisants", "Pas assez de points pour acheter cet article.")

    def determine_purchase_type(self, index):
        if index < len(self.themes_images):
            return "theme"
        elif index < len(self.themes_images) + len(self.items_images):
            return "item"
        elif index < len(self.themes_images) + len(self.items_images) + len(self.money_images):
            return "money"
        elif index < len(self.themes_images) + len(self.items_images) + len(self.money_images) + len(self.charity_images):
            return "charity"
        else:
            return "unknown"

    def process_theme_purchase(self,index):

        theme_names = ["green", "blue", "pink", "yellow", "default"]
        french_theme_names = ["vert", "bleu", "rose", "jaune", "par défaut"]

        if index < len(theme_names):
            # insert logic to change theme
            selected_theme_fr = french_theme_names[index]
            theme.change_theme(theme_names[index])
            tk.messagebox.showinfo("Achat réussi", f"Merci de re-démarrer l'app pour appliquer le thème : {selected_theme_fr}.")

        else:
            print("Invalid theme selection.")