class MetroAppUI(tk.Frame):
    def __init__(self, master=None, image_path=None):
        super().__init__(master)
        self.master = master
        self.master.title("Metro App")
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.image_path = image_path

        # this sets the size of the tkinter window
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(width=True, height=True)

        # initialize the metro image display
        self.init_image_display()
        self.create_quit_button()
        self.plot_stations()

    def plot_stations(self):
        file_path = 'Version1/pospoints.txt'
        plot_stations_on_canvas(self.canvas, file_path)

    def init_image_display(self):
        # we open the original image stored in data
        self.image_original = Image.open(self.image_path)
        # this is to calculte the ratio between our image's width and height
        self.image_ratio = self.image_original.width / self.image_original.height

        self.canvas = tk.Canvas(self.master, background=self.master.cget('bg'), bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind('<Configure>', self.show_full_image)
