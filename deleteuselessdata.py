# Lire le fichier en mode lecture
with open("Version2_Version3/data/stop_times.txt","r") as f:
    lines = f.readlines()

# Écrire seulement les lignes qui commencent par 'IDFM:RATP' dans le fichier
with open("Version2_Version3/data/stop_times.txt","w") as f:
    for line in lines:
        if line.split(':')[1] == 'RATP':
            f.write(line)