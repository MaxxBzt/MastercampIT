
theme_background = None
theme_frame = None
theme_stations = None
theme_menu = None
theme_hover = None
theme_tab = None



def change_theme(theme):
    global theme_background
    global theme_frame
    global theme_stations
    global theme_menu
    global theme_hover
    global theme_tab

    with open("Data/theme.txt", "w") as f:
        f.write(theme)

    if theme == "purple" or theme == "default":
        theme_background = ("#FEF7FF", "#323232")
        theme_frame = ("#ECDCFF", "#5c497e")
        theme_stations = ("#846AAF", "#8C74A7")
        theme_menu = ("#69548D","#240E45")
        theme_hover = ("#7C66A3","#4c1c7b")
        theme_tab = ("#a390c3","#a390c3")
        return
    if theme == "green":
        theme_background = ("#E7F8E7", "#2B5C2B")
        theme_frame = ("#C4ECC4", "#1E4B1E")
        theme_stations = ("#A8D8A8", "#1B4721")  # Darkened for better contrast
        theme_menu = ("#92C692", "#104016")  # Darkened for better contrast
        theme_hover = ("#7BAA7B", "#133B13")
        theme_tab = ("#9EC79B", "#1B4721")
        return
    if theme == "blue":
        theme_background = ("#D8E8FF", "#1B2735")  # Darkened for better contrast
        theme_frame = ("#B0D4FF", "#142030")  # Darkened for better contrast
        theme_stations = ("#9FC7FF", "#101B25")  # Darkened for better contrast
        theme_menu = ("#8BB6FF", "#122e3c")  # Darkened for better contrast
        theme_hover = ("#7AA4FF", "#0A131A")  # Darkened for better contrast
        theme_tab = ("#9FC7FF", "#101B25")
        return
    if theme == "pink":
        theme_background = ("#ffe7fa", "#5A2C47")
        theme_frame = ("#FFC3E7", "#4A233B")
        theme_stations = ("#FFB1D6", "#3A1A2F")  # Darkened for better contrast
        theme_menu = ("#FF9DC9", "#311626")  # Darkened for better contrast
        theme_hover = ("#FF89B8", "#1b0d11")  # Darkened for better contrast
        theme_tab = ("#FFB1D6", "#3A1A2F")
        return
    if theme == "yellow":
        theme_background = ("#feffe5", "#3F3B1D")  # Replaced with a more pleasing dark color
        theme_frame = ("#FFF1A1", "#2D2A14")  # Replaced with a more pleasing dark color
        theme_stations = ("#FFE877", "#252211")  # Replaced with a more pleasing dark color
        theme_menu = ("#FFDD55", "#535504")  # Replaced with a more pleasing dark color
        theme_hover = ("#FFCC33", "#090704")  # Replaced with a more pleasing dark color
        theme_tab = ("#FFE877", "#252211")
        return
