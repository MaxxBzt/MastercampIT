import pandas as pd
from PIL import Image, ImageDraw, ImageTk
import os

def plot_stations_on_canvas(canvas, file_path):
    version1_path = os.path.join(os.getcwd(), 'Version1')
    if os.path.isdir(version1_path):
        print("Contents of Version1 directory:", os.listdir(version1_path))
    else:
        print("The Version1 directory does not exist.")
    
    if not os.path.isfile(file_path):
        print(f"Le fichier {file_path} n'a pas été trouvé. Vérifiez le chemin du fichier.")
    else:
        data = pd.read_csv(file_path, delimiter=';', header=None, names=['x', 'y', 'station'])

        data['station'] = data['station'].str.replace('@', ' ')

        print("First 5 rows of the DataFrame:")
        print(data.head())

        map_image_path = 'paris_map.png.jpg'  
        if not os.path.isfile(map_image_path):
            print(f"L'image de la carte {map_image_path} n'a pas été trouvée. Vérifiez le chemin de l'image.")
        else:
            map_image = Image.open(map_image_path)
            draw = ImageDraw.Draw(map_image)

            for index, row in data.iterrows():
                x, y = row['x'], row['y']
                draw.ellipse((x-5, y-5, x+5, y+5), fill='blue', outline='blue')

            # Convert PIL image to Tkinter PhotoImage
            map_photo = ImageTk.PhotoImage(map_image)
            canvas.image = map_photo  # Keep a reference to prevent garbage collection
            canvas.create_image(0, 0, anchor='nw', image=map_photo)

            # Notify Tkinter to redraw the canvas
            canvas.update()
