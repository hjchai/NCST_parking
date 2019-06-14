# Steps for data processing
0. run 'extract_tax_poly.py' to check if the network is covered fully by the tazs.
1. run 'dataset_split.py' to split big matsim dataset into small dataset for each city.
 * Only persons have a from_point or a to_point within the TAZs boundary are kept.
2. run 'demand_matsim2sumo.py' to convert matsim format to sumo format.

# notes 
1. san_francisco all: 2811700 trips, 8xxxxx person
2. workflow:
 * parseXML()->trips: list of dict->sort trips->trips_sorted->createAndSaveTripXML(): 
 save trips_sorted to xml->randomizeOriginDestination(): randomizeOD->trips_sorted_randomized->
 createAndSaveTripXML(): save trips_sorted_randomized to xml->createTripXML():->createTrip()