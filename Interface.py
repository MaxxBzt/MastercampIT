import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import os


class MetroAppUI(tk.Frame):
    def __init__(self, master=None, image_path=None, points_txt=None, metro_graph=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.image_path = image_path
        self.points_txt = points_txt
        self.metro_graph = metro_graph
        # dictionary that will remember which point is linked to which coordinates
        self.coord_dict = {}

        # this sets the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        self.create_quit_button()
        # Initialize the metro image display
        self.init_image_display()
        self.points_data = self.load_points()

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

    def load_points(self):
        if not os.path.isfile(self.points_txt):
            print(f"Le fichier {self.points_txt} n'a pas été trouvé. Vérifiez le chemin du fichier.")
            return pd.DataFrame(columns=['x', 'y', 'station'])
        else:
            data = pd.read_csv(self.points_txt, delimiter=';', header=None, names=['x', 'y', 'station'])
            data['station'] = data['station'].str.replace('@', ' ')
            return data

    def init_image_display(self):
        # we open the original image stored in data
        self.image_original = Image.open(self.image_path)
        # this is to calculte the ratio between our image's width and height
        self.image_ratio = self.image_original.width / self.image_original.height

        self.canvas = tk.Canvas(self.master, background=self.master.cget('bg'), bd=0, highlightthickness=0,
                                relief='ridge')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind('<Configure>', self.show_full_image)

    # this manages how the image will be shown on the window
    def show_full_image(self, event):
        canvas_width = event.width
        canvas_height = event.height

        # if the window of the user is larger than the image
        if canvas_width / canvas_height > self.image_ratio:  # Canvas is wider than the image
            new_height = canvas_height
            new_width = int(new_height * self.image_ratio)
        # if it's smaller
        else:
            new_width = canvas_width
            new_height = int(new_width / self.image_ratio)

        # we resize image
        resized_image = self.image_original.resize((new_width, new_height), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(resized_image)

        # we clear the canvas and place the resized image center
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            anchor='center',
            image=self.img
        )

        # this is to calculate the scaling factor of our metro image
        original_width, original_height = self.image_original.size
        scale_x = new_width / original_width
        scale_y = new_height / original_height

        # Calculate offset to center the image on the canvas
        offset_x = (canvas_width - new_width) // 2
        offset_y = (canvas_height - new_height) // 2

        # STARTING TO DRAW POINTS ON CANVAS
        for index, row in self.points_data.iterrows():
            x, y, station = row['x'], row['y'], row['station']

            # Convert the coordinates to the resized image coordinates
            # the offset allows it to be centered on the image. else the points are on the left
            new_x = x * scale_x + offset_x
            new_y = y * scale_y + offset_y

            # We really draw points
            point = self.canvas.create_oval(
                new_x - 5, new_y - 5, new_x + 5, new_y + 5,
                fill='white', outline='black'
            )

            # we store the point and which tuple of coordinates
            self.coord_dict[point] = (x, y, station)
            # when point is created, you give it and bind it with the print_coordinates function when clicked left
            # in tkinter, to refer to left mouse click it's <Button-1>, middle mouse 2, right 3
            self.canvas.tag_bind(point, "<Button-1>", self.find_station_id)

    def create_quit_button(self):
        self.quit = tk.Button(self.master, text="QUIT", fg="red", bg="black", command=self.master.destroy)
        self.quit.pack(side="bottom")
