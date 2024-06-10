import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import os

class MetroAppUI(tk.Frame):
    def __init__(self, master=None, image_path=None, points_txt=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.points_txt = points_txt
    
        # this sets the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        self.create_quit_button()

        self.image_path = image_path

        # Initialize the metro image display
        self.init_image_display()

        self.points_data = self.load_points()


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

        
        self.canvas = tk.Canvas(self.master, background=self.master.cget('bg'), bd=0, highlightthickness=0, relief='ridge')
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

        # this is to calculate the scalling factor of our metro image
        original_width, original_height = self.image_original.size
        scale_x = new_width / original_width
        scale_y = new_height / original_height

        # Calculate offset to center the image on the canvas
        offset_x = (canvas_width - new_width) // 2
        offset_y = (canvas_height - new_height) // 2

        # STARTING TO DRAW POINTS ON CANVAS
        for index, row in self.points_data.iterrows():
            x, y = row['x'], row['y']

            # Convert the coordinates to the resized image coordinates
            # the offset allows it to be centered on the image. else the points are on the left
            new_x = x * scale_x + offset_x
            new_y = y * scale_y + offset_y

            # We really draw points
            self.canvas.create_oval(
                new_x - 5, new_y - 5, new_x + 5, new_y + 5,
                fill='white', outline='black'
            )

    def create_quit_button(self):
        self.quit = tk.Button(self.master, text="QUIT", fg="red", bg="black", command=self.master.destroy)
        self.quit.pack(side="bottom")

