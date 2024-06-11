import tkinter as tk
import customtkinter as ctk

def on_custom_button_click():
    print("calculate button clicked")

# Create main window
root = ctk.CTk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.title("Metro Map")
root_color = root.cget("bg")

# Configure appearance
ctk.set_appearance_mode("automatic")
ctk.set_default_color_theme("blue")

# Départ   
src_label = tk.Label(root, text="Position de départ:", bg=root_color, font=("Arial", 16))
src_label.pack(anchor='w', pady=(30,10), padx=(50, 10))  
src_entry= ctk.CTkEntry(root, font=("Arial", 16), width=450, height=40)
src_entry.pack(anchor='w', pady=15, padx=(50, 10))  

# Destination
des_label = tk.Label(root, text="Destination:", bg=root_color, font=("Arial", 16))
des_label.pack(anchor='w', pady=10, padx=(50, 10)) 
des_entry = ctk.CTkEntry(root, font=("Arial", 16), width=450, height=40)
des_entry.pack(anchor='w', pady=30, padx=(50, 10))  

# Calculate button
calc_button = ctk.CTkButton(root, text="Calculer l'iténéraire", command=on_custom_button_click, font=("Arial", 20))
calc_button.pack(anchor='w', pady=10, padx=(50, 10))  

# Run the application
root.mainloop()

def main():
    on_custom_button_click()