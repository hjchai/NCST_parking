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
3. Command for sumo visualization:
 * python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py -n ../../san_francisco.net.xml -m speed,speed -i edgedata_traffic_1.0_drop-off.xml,edgedata_traffic_1.0_drop-off.xml -v -o speed.png --min-color-value 3 --max-color-value 15 --colormap '#0:#c00000,.25:#804040,.5:#808080,.75:#408040,1:#00c000' -o ../plots/edge_speed_1.0.png --title "100% dropoff"
4. Command to run multiple simulations 
 * sumo -c san_francisco.sumo.cfg -r '../san_francisco.rou.xml,trip_0.01_with_0.5_drop-off_0.5_drop-off_only.xml'
 * preferable done in python