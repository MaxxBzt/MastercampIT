terminus = {'1': [['La Défense (Grande Arche)', 'IDFM:RATP:124742-C01371-COU_RATP_5083931_1078871_346'], ['Château de Vincennes', 'IDFM:RATP:123210-C01371-COU_RATP_5083931_1078872_225']], '2': [['Porte Dauphine (Maréchal de Lattre de Tassigny)', 'IDFM:RATP:125803-C01372-COU_RATP_5084004_2991124_69'], ['Nation', 'IDFM:RATP:125803-C01372-COU_RATP_5083991_3120391_64']], '3': [['Gallieni (Parc de Bagnolet)', 'IDFM:RATP:124987-C01373-COU_RATP_5083967_912354_268'], ['Pont de Levallois-Bécon', 'IDFM:RATP:107709-C01373-COU_RATP_4828788_95500_88']], '4': [['Bagneux - Lucie Aubrac', 'IDFM:RATP:130697-C01374-COU_RATP_5097971_3155741_427'], ['Porte de Clignancourt', 'IDFM:RATP:130697-C01374-COU_RATP_5097971_3155742_423']], '5': [["Place d'Italie", 'IDFM:RATP:124363-C01375-COU_RATP_5084015_3120421_71'], ['Bobigny-Pablo-Picasso', 'IDFM:RATP:124363-C01375-COU_RATP_5084015_3120422_84']], '6': [['Nation', 'IDFM:RATP:130780-C01376-COU_RATP_5096756_1193703_343'], ['Charles de Gaulle-Etoile', 'IDFM:RATP:130780-C01376-COU_RATP_5086609_3130586_67']], '7': [['La Courneuve-8-Mai-1945', 'IDFM:RATP:110316-C01377-COU_RATP_5077478_912373_97'], ["Mairie d'Ivry", 'IDFM:RATP:107499-C01377-COU_RATP_5083921_2467805_113'], ['Villejuif-Louis Aragon', 'IDFM:RATP:124252-C01377-COU_RATP_5084057_2467804_7']], '8': [['Balard', 'IDFM:RATP:123226-C01378-COU_RATP_5084076_795507_221'], ['Créteil-Pointe du Lac', 'IDFM:RATP:112671-C01378-COU_RATP_4831051_795505_227']], '9': [['Mairie de Montreuil', 'IDFM:RATP:124963-C01379-COU_RATP_5084090_3120452_203'], ['Pont de Sèvres', 'IDFM:RATP:124963-C01379-COU_RATP_5084090_1652933_234']], '10': [["Gare d'Austerlitz", 'IDFM:RATP:108698-C01380-COU_RATP_4832839_917606_101'], ['Boulogne Pont de Saint-Cloud', 'IDFM:RATP:108698-C01380-COU_RATP_4832839_296022_107']], '11': [['Mairie des Lilas', 'IDFM:RATP:127519-C01381-COU_RATP_5095215_440174_283'], ['Châtelet', 'IDFM:RATP:127519-C01381-COU_RATP_5094171_912409_240']], '12': [["Mairie d'Issy", 'IDFM:RATP:125866-C01382-COU_RATP_5083985_2811696_106'], ["Mairie d'Aubervilliers", 'IDFM:RATP:125866-C01382-COU_RATP_5083985_2811694_124']], '13': [['Châtillon Montrouge', 'IDFM:RATP:121404-C01383-COU_RATP_5083947_2467829_185'], ['Saint-Denis-Université', 'IDFM:RATP:119479-C01383-COU_RATP_5087122_2467827_145'], ['Asnières-Gennevilliers Les Courtilles', 'IDFM:RATP:119479-C01383-COU_RATP_5087122_2467826_165']], '14': [['Olympiades', 'IDFM:RATP:130145-C01384-COU_RATP_5095126_3164005_118'], ['Mairie de Saint-Ouen', 'IDFM:RATP:127173-C01384-COU_RATP_5095126_3164011_225']], '3B': [['Porte des Lilas', 'IDFM:RATP:119390-C01386-COU_RATP_4832832_651522_28'], ['Gambetta', 'IDFM:RATP:119390-C01386-COU_RATP_4832832_651521_31']], '7B': [['Louis Blanc', 'IDFM:RATP:123050-C01387-COU_RATP_4831065_651583_28'], ['Pré-Saint-Gervais', 'IDFM:RATP:123050-C01387-COU_RATP_4831062_651584_119']]}

# Récupérer toutes les durées des metros arrivant à ces destination
# Utilisation de la librairies pandas pour la manipulation de données

import pandas as pd

file_route = '../Version2_Version3/data/routes.txt'
file_trips = '../Version2_Version3/data/trips.txt'
file_stop_times = '../Version2_Version3/data/stop_times.txt'
file_stops = '../Version2_Version3/data/stops.txt'

# ligne contenue dans route.txt : IDFM:C01371,IDFM:Operator_100,1,1,,1,,FFBE00,000000,
# Nous allons récupérer les colonnes route_id et route_short_name
routes = pd.read_csv(file_route, usecols=['route_id', 'route_short_name', 'route_type'])


# ligne dans trip.txt : IDFM:C00467,IDFM:1,IDFM:CARSLACROIX:105407-C00467-51-C00467-3939-511544,La Tour,,1,,,0,0
# Nous allons récupérer les colonnes trip_id, route_id et la direction
trips = pd.read_csv(file_trips, usecols=['trip_id', 'route_id', 'trip_headsign'])

# ligne dans stop_times.txt : IDFM:RATP:124742-C01371-COU_RATP_5083931_1078871_346,IDFM:RATP:124742-C01371-COU_RATP_5083931_1078871_346,1,00:00:00,00:00:00,0,0
# Nous allons récupérer les colonnes trip_id, arrival_time,stop_id
stop_times = pd.read_csv(file_stop_times, usecols=['trip_id', 'arrival_time', 'stop_id'])

# ligne dans stops.txt : IDFM:RATP:124742-C01371-COU_RATP_5083931_1078871_346,La Défense (Grande Arche),48.892,2.236
# Nous allons récupérer les colonnes stop_id et stop_name
stops = pd.read_csv(file_stops, usecols=['stop_id', 'stop_name'])

# Nous voulons récupérer les temps de trajet que pour les arrets qui sont stocké dans la variable terminus




# Fusionner routes et trips sur 'route_id'
route_trips = pd.merge(routes, trips, on='route_id')

# Filtrer pour ne garder que les lignes où 'route_type' est 1 (métro)
route_trips = route_trips[route_trips['route_type'] == 1]

# Filtrer pour ne garder que les lignes où 'trip_headsign' est un terminus
terminus_list = [item[0] for sublist in terminus.values() for item in sublist]
route_trips = route_trips[route_trips['trip_headsign'].isin(terminus_list)]

# Fusionner avec stop_times sur 'trip_id'
route_trips_times = pd.merge(route_trips, stop_times, on='trip_id')

# Fusionner avec stops sur 'stop_id'
final_df = pd.merge(route_trips_times, stops, on='stop_id')

# Filtrer pour ne garder que les lignes où 'stop_name' est un terminus
final_df = final_df[final_df['stop_name'].isin(terminus_list)]

# Le DataFrame final contient l'heure d'arrivée de chaque métro au terminus de chaque ligne
final_df.to_csv('output.csv', sep='\t', index=False)



def check_same_line(row):
    # Pour chaque ligne, obtenir la liste des terminus pour la ligne de cette ligne
    terminus_for_this_line = [item[0] for item in terminus[row['route_short_name']]]
    # Vérifier si le trip_headsign et le stop_name sont tous deux dans la liste des terminus
    # et si trip_headsign n'est pas égal à stop_name
    return row['trip_headsign'] in terminus_for_this_line and row['stop_name'] in terminus_for_this_line and row['trip_headsign'] != row['stop_name']


# Appliquer la fonction à chaque ligne
final_df['same_line'] = final_df.apply(check_same_line, axis=1)

# Filtrer le DataFrame pour ne garder que les lignes où 'same_line' est True
final_df = final_df[final_df['same_line']]

# Supprimer la colonne 'same_line' car elle n'est plus nécessaire
final_df = final_df.drop(columns=['same_line'])


# Le DataFrame final contient l'heure d'arrivée de chaque métro au terminus de chaque ligne, et seulement pour les lignes où le trip_headsign et le stop_name appartiennent à la même ligne
final_df.to_csv('output_2.csv', sep='\t', index=False)
final_df = final_df.drop(columns=['route_type','route_id', 'trip_id', 'stop_id'])



# Trier les lignes en fonction des horaires d'arrivée sans mélanger les lignes de métro et les terminus
final_df = final_df.sort_values(by=['route_short_name', 'trip_headsign', 'arrival_time'])

final_df.to_excel('output_2.xlsx', index=False)

