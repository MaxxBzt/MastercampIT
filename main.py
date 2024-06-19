import time



import networkx as nx
import tkinter as tk
import customtkinter as ctk
from UI.InterfaceV1 import MetroAppUI
from Data.ExtractData import dataversion1, dataversion2
from Data.utilities import metro_lines_info



metro_image_path = "Version1/metrof_r.png"
file_path = 'Version1/pospoints.txt'

def choose_data(version):
    if version == "Version 1":
        return dataversion1()
    elif version == "Version 2":
        return dataversion2()

def start_app(version, app):
    # Choose the data version
    metro_graph = choose_data(version)
    if metro_graph is None:
        print(f"Failed to load data for {version}")
        return

    # Destroy the current window
    app.destroy()

    # Create a new instance of MetroAppUI with the selected data version
    root = tk.Tk()
    MetroAppUI(master=root, image_path=metro_image_path, points_txt=file_path, metro_graph=metro_graph, metro_line_image=metro_lines_info).mainloop()


def choose_data_menu():
    # Initialize the main window
    app = ctk.CTk()
    app.geometry("650x500")
    app.title("Metro, Efrei, Dodo - Choose Data")

    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

    # Create the main title label
    title_label = ctk.CTkLabel(app, text="Metro, Efrei, Dodo", font=ctk.CTkFont(size=24, weight="bold"))
    title_label.pack(pady=20)

    # Create frame for buttons and descriptions
    frame = ctk.CTkFrame(app)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Configure the columns to distribute the extra space equally
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)



    # Create Version 1 button and description
    button1 = ctk.CTkButton(frame, text="Version 1", command=lambda: start_app("Version 1", app))
    # button1 = ctk.CTkButton(frame, text="Version 1", command=test_callback)  # Temporary test callback
    button1.grid(row=0, column=0, padx=20, pady=10, sticky="ew")


    description1 = ctk.CTkLabel(frame, text="Description for Version 1:\n\n"
                                            "This version is the most basic one with a map of the metro"
                                            " and the possibility to calculate the shortest path between two stations.\n"
                                            "The graph is undirected. This version is efficient & quick but lacks updates or new data.",
                                wraplength=250, anchor="nw", justify="left")
    description1.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

    # Create Version 2 button and description
    button2 = ctk.CTkButton(frame, text="Version 2", command=lambda: start_app("Version 2", app))
    # button2 = ctk.CTkButton(frame, text="Version 2", command=test_callback)  # Temporary test callback
    button2.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

    description2 = ctk.CTkLabel(frame, text="Description for Version 2:\n\n"
                                            "This version includes data from IDFM 2024, the graph is directed and includes more information.\n"
                                            "This version is more complex, and less efficient but includes more data and is more accurate.",
                                wraplength=250, anchor="nw", justify="left")
    description2.grid(row=1, column=1, padx=20, pady=5, sticky="nsew")

    # Create developer names label
    developers_label = ctk.CTkLabel(app, text="Beautifully coded by our team: Yoke, Maxime, Roxanne, Mélissa & Audrey",
                                    font=ctk.CTkFont(size=12))
    developers_label.pack(side="bottom", pady=20)

    # Run the application
    app.mainloop()

choose_data_menu()