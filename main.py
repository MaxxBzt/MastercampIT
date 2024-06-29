import random
import time
import timeit

import networkx as nx
import tkinter as tk
import customtkinter as ctk
from cryptography.fernet import Fernet

from Graph.shortestpath import dijkstra, bellman_ford
from UI.InterfaceV1 import MetroAppUIV1
from UI.InterfaceV2 import MetroAppUIV2
from Data.ExtractData import dataversion1, dataversion2
from Data.utilities import metro_lines_info

# Theme colors
import UI.theme as theme


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
    root = ctk.CTk()
    if version == "Version 1":
        MetroAppUIV1(master=root, image_path=metro_image_path, points_txt=file_path, metro_graph=metro_graph,
                     metro_line_image=metro_lines_info).mainloop()
    elif version == "Version 2":
        MetroAppUIV2(master=root, metro_graph=metro_graph, metro_line_image=metro_lines_info).mainloop()


def choose_data_menu():
    theme.change_theme("pink")

    # Initialize the main window
    app = ctk.CTk()
    app.geometry("650x500")
    app.title("Metro, Efrei, Dodo - Choosir la version")
    app.configure(fg_color=theme.theme_background)

    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

    # Create the main title label
    title_label = ctk.CTkLabel(app, text="Metro, Efrei, Dodo", font=ctk.CTkFont(size=24, weight="bold"))
    title_label.pack(pady=20)

    # Create frame for buttons and descriptions
    frame = ctk.CTkFrame(app, fg_color=theme.theme_frame)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Configure the columns to distribute the extra space equally
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    # Create Version 1 button and description
    button1 = ctk.CTkButton(frame, text="Version 1",fg_color=(theme.theme_menu),  hover_color=(theme.theme_hover), command=lambda: start_app("Version 1", app))
    # button1 = ctk.CTkButton(frame, text="Version 1", command=test_callback)  # Temporary test callback
    button1.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    description1 = ctk.CTkLabel(frame, text="Description pour la Version 1:\n\n"
                                            "Cette version est la plus basique avec un plan du métro"
                                            " et la possibilité de calculer le chemin le plus court entre deux stations.\n"
                                            "Le graphique n'est pas orienté. Cette version est efficace et rapide mais manque de mises à jour ou de nouvelles données.",
                                wraplength=250, anchor="nw", justify="left")
    description1.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

    # Create Version 2 button and description
    button2 = ctk.CTkButton(frame, text="Version 2", fg_color=(theme.theme_menu), hover_color=(theme.theme_hover), command=lambda: start_app("Version 2", app))
    # button2 = ctk.CTkButton(frame, text="Version 2", command=test_callback)  # Temporary test callback
    button2.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

    description2 = ctk.CTkLabel(frame, text="Description pour la Version 2:\n\n"
                                            "Cette version inclut les données d'IDFM 2024, le graphique est orienté et comprend plus d'informations.\n"
                                            "Cette version est plus complexe et moins efficace mais inclut plus de données et est plus précise.",
                                wraplength=250, anchor="nw", justify="left")
    description2.grid(row=1, column=1, padx=20, pady=5, sticky="nsew")

    # Create developer names label
    developers_label = ctk.CTkLabel(app,
                                    text="Magnifiquement codé par notre équipe : Yoke, Maxime, Roxanne, Mélissa & Audrey\n"
                                         "Using IDFM 2024 data",
                                    font=ctk.CTkFont(size=12))
    developers_label.pack(side="bottom", pady=20)

    # Run the application
    app.mainloop()


choose_data_menu()
