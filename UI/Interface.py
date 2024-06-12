import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import os
import customtkinter as ctk

class MetroAppUI(tk.Frame):
    def __init__(self, master=None, image_path=None, points_txt=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.points_txt = points_txt

        # Set the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        self.image_path = image_path

        # Create the main window elements
        self.create_main_layout()

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

    def create_main_layout(self):
        # Create a frame for the controls
        self.control_frame = ctk.CTkFrame(self.master)
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Create the canvas for the image
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side="right", fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, background=self.master.cget('bg'), bd=0, highlightthickness=0, relief='ridge')
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
            x, y = row['x'], row['y']

            # Convert the coordinates to the resized image coordinates
            new_x = x * scale_x + offset_x
            new_y = y * scale_y + offset_y

            # Draw points
            self.canvas.create_oval(
                new_x - 5, new_y - 5, new_x + 5, new_y + 5,
                fill='white', outline='black'
            )

    def create_quit_button(self):
        self.quit = ctk.CTkButton(self.control_frame, text="QUIT", fg_color="red", command=self.master.destroy)
        self.quit.pack(side="bottom", pady=10)

    def create_input_controls(self):
        # Configure appearance
        ctk.set_appearance_mode("automatic")
        ctk.set_default_color_theme("blue")
        
        # Depart
        src_label = ctk.CTkLabel(self.control_frame, text="Position de départ:", font=("Arial", 16))
        src_label.pack(anchor='w', pady=(30, 10), padx=(10, 10))
        self.src_entry = ctk.CTkEntry(self.control_frame, font=("Arial", 16), width=300, height=40)
        self.src_entry.pack(anchor='w', pady=15, padx=(10, 10))

        # Destination
        des_label = ctk.CTkLabel(self.control_frame, text="Destination:", font=("Arial", 16))
        des_label.pack(anchor='w', pady=10, padx=(10, 10))
        self.des_entry = ctk.CTkEntry(self.control_frame, font=("Arial", 16), width=300, height=40)
        self.des_entry.pack(anchor='w', pady=15, padx=(10, 10))

        # Calculate button
        calc_button = ctk.CTkButton(self.control_frame, text="Calculer l'itinéraire", command=self.button_clicked, font=("Arial", 20))
        calc_button.pack(anchor='w', pady=10, padx=(10, 10))

    def button_clicked(self):
        print("Calculate button clicked")

