import os
import matplotlib.pyplot as plt

drop_off_percentage = [0.3]#[0.0, 0.1, 0.2, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]#[0.5]
drop_off_only_percentage = [0.0, 0.1, 0.2, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

city_path = "../cities/san_francisco/"
scenario = "Scenario_Set_2"


for i in drop_off_only_percentage:
    for j in drop_off_percentage:
        if scenario[-1] == '2':
            command = "python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py \
                        -n " + city_path + "san_francisco.net.xml -m occupancy,occupancy \
                        -i " + city_path + scenario + "/results/" + str(j) + "_drop-off/edgedata_traffic_" + str(j) + "_drop-off_" + str(i) + "_drop-off_only.xml,"\
                             + city_path + scenario + "/results/" + str(j) + "_drop-off/edgedata_traffic_" + str(j) + "_drop-off_" + str(i) + "_drop-off_only.xml \
                        -v --min-color-value 0 --max-color-value 5.0 \
                        --colormap '#0:#00c000,.25:#408040,.5:#808080,.75:#804040,1:#c00000' \
                        -o " + city_path + scenario + "/plots/" + str(j) + "_drop-off/occupancy_" + str(i) + "_drop-off_only.png \
                        --title '" + str (100 * i) + "% dropoff only' --xlim 500,4500 --xlabel '[m]' --ylabel '[m]'"
        elif scenario[-1] == '1':
            command = "python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py \
                        -n " + city_path + "san_francisco.net.xml -m occupancy,occupancy \
                        -i " + city_path + scenario + "/results/edgedata_traffic_" + str(j) + "_drop-off.xml," \
                             + city_path + scenario + "/results/edgedata_traffic_" + str(j) + "_drop-off.xml \
                        -v --min-color-value 0 --max-color-value 1.0 \
                        --colormap '#0:#00c000,.25:#408040,.5:#808080,.75:#804040,1:#c00000' \
                        -o " + city_path + scenario + "/plots/occupancy_" + str(j) + "_drop-off.png \
                        --title '" + str(100 * j) + "% dropoff' --xlim 500,4500 --xlabel '[m]' --ylabel '[m]'"
        os.system(command)
#