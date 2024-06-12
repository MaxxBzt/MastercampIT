import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import os
import customtkinter as ctk
from Graph.shortestpath import dijkstra


class MetroAppUI(tk.Frame):
    def __init__(self, master=None, image_path=None, points_txt=None, metro_graph=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.points_txt = points_txt
        self.image_path = image_path
        self.metro_graph = metro_graph
        self.selected_station_arrive_id = None
        self.selected_station_depart_id = None

        # dictionary that will remember which point is linked to which coordinates
        self.coord_dict = {}

        # Set the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        # Create the main window elements
        self.create_main_layout()

        # Initialize the metro image display
        self.init_image_display()

        self.points_data = self.load_points()

    ''' UI UTILITARY FUNCTIONS -- functions useful in the UI interface '''

    def find_station_id(self, event):
        # Get the id of the clicked object
        point_id = event.widget.find_closest(event.x, event.y)[0]
        if point_id in self.coord_dict:
            x, y, station_name = self.coord_dict[point_id]
            print(f"Coordonnées du point cliquées: ({x}, {y}, {station_name})")
        else:
            print("Vous avez cliqué sur un point inconnu.")

        # data=True get us : (node, node_attribute_dict)
        #        node = the node ID & node_attribute_dict a dictionary of the node's attributes
        # without it, we only get the node's ID, not attributes
        for node in self.metro_graph.nodes(data=True):
            if node[1]['name'] == station_name:
                print("Station ID:", node[0])
                break
        else:
            print("La station ", station_name, "n'a pas été trouvée.")

    def get_station_id_from_name(self, station_name):
        for node in self.metro_graph.nodes(data=True):
            if node[1]['name'] == station_name:
                return node[0]
        return None  # Return None if station name not found

    def create_quit_button(self):
        self.quit = ctk.CTkButton(self.control_frame, text="QUIT", fg_color="red", command=self.master.destroy)
        self.quit.pack(side="bottom", pady=10)


    ''' UI MANDATORY FUNCTIONS -- functions that do big things in UI '''

    def load_points(self):
        if not os.path.isfile(self.points_txt):
            print(f"Le fichier {self.points_txt} n'a pas été trouvé. Vérifiez le chemin du fichier.")
            return pd.DataFrame(columns=['x', 'y', 'station'])
        else:
            data = pd.read_csv(self.points_txt, delimiter=';', header=None, names=['x', 'y', 'station'])
            data['station'] = data['station'].str.replace('@', ' ')
            return data

    def create_main_layout(self):
        # Create a frame for the controls
        self.control_frame = ctk.CTkFrame(self.master)
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Create the canvas for the image
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, background=self.master.cget('bg'), bd=0, highlightthickness=0,
                                relief='ridge')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind('<Configure>', self.show_full_image)

        self.create_quit_button()
        self.create_input_controls()

    def init_image_display(self):
        # Open the original image stored in data
        self.image_original = Image.open(self.image_path)
        # Calculate the ratio between our image's width and height
        self.image_ratio = self.image_original.width / self.image_original.height

    def show_full_image(self, event):
        canvas_width = event.width
        canvas_height = event.height

        # If the window of the user is larger than the image
        if canvas_width / canvas_height > self.image_ratio:  # Canvas is wider than the image
            new_height = canvas_height
            new_width = int(new_height * self.image_ratio)
        else:
            new_width = canvas_width
            new_height = int(new_width / self.image_ratio)

        # Resize image
        resized_image = self.image_original.resize((new_width, new_height), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(resized_image)

        # Clear the canvas and place the resized image center
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            anchor='center',
            image=self.img
        )

        # Calculate the scaling factor of our metro image
        original_width, original_height = self.image_original.size
        scale_x = new_width / original_width
        scale_y = new_height / original_height

        # Calculate offset to center the image on the canvas
        offset_x = (canvas_width - new_width) // 2
        offset_y = (canvas_height - new_height) // 2

        # Draw points on canvas
        for index, row in self.points_data.iterrows():
            x, y, station = row['x'], row['y'], row['station']

            # Convert the coordinates to the resized image coordinates
            new_x = x * scale_x + offset_x
            new_y = y * scale_y + offset_y

            # Draw points
            point = self.canvas.create_oval(
                new_x - 5, new_y - 5, new_x + 5, new_y + 5,
                fill='white', outline='black'
            )
            # Store the point and its corresponding coordinates
            self.coord_dict[point] = (x, y, station)
            # Bind the point with the find_station_id function on left mouse click
            self.canvas.tag_bind(point, "<Button-1>", self.find_station_id)

    def on_src_entry_change(self, src_entry):
        # here we convert the input of user to lowercase in case he does maj
        user_input = self.src_entry.get().strip().lower()

        # we start the search of station when we have 3 characters in the input
        if len(user_input) < 3:
            self.dropdown_menu_depart.pack_forget()
            return

        self.dropdown_menu_depart.delete(0, tk.END)
        matching_stations = []

        for node in self.metro_graph.nodes(data=True):
            if user_input in node[1]['name'].lower():
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

        user_input = self.des_entry.get().strip().lower()

        # we start the search of station when we have 3 characters in the input
        if len(user_input) < 3:
            self.dropdown_menu_arrive.pack_forget()
            return

        self.dropdown_menu_arrive.delete(0, tk.END)
        matching_stations = []

        for node in self.metro_graph.nodes(data=True):
            if user_input in node[1]['name'].lower():
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
        calc_button = ctk.CTkButton(self.control_frame, text="Calculer l'itinéraire", command=self.calculate_itinerary,
                                    font=("Arial", 20))
        calc_button.pack(anchor='w', pady=10, padx=(10, 10))

    def calculate_itinerary(self):
        shortest_path = dijkstra(self.metro_graph, self.selected_station_depart_id, self.selected_station_arrive_id)
        print("The shortest path is:")
        print(shortest_path[0])
        print("The duration of the shortest path is:")
        print(shortest_path[1] // 60, "minutes", shortest_path[1] % 60, "secondes")

    def button_clicked(self):
        print("Calculate button clicked")
