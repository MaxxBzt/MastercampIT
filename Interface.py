import tkinter as tk
from PIL import Image, ImageTk

class MetroAppUI(tk.Frame):
    def __init__(self, master=None, image_path=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

    
        # this sets the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        self.create_quit_button()

        self.image_path = image_path
        
        # initialize the metro image display
        self.init_image_display()


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
        else:  # Canvas is narrower than the image
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

    def create_quit_button(self):
        self.quit = tk.Button(self.master, text="QUIT", fg="red", bg="black", command=self.master.destroy)
        self.quit.pack(side="bottom")


metro_image_path = "/Users/nolwen/Documents/GitHub/MastercampIT/Version1/metrof_r.png"

root = tk.Tk()
app = MetroAppUI(master=root, image_path=metro_image_path)
app.mainloop()

