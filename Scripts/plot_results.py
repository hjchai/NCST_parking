import os
import matplotlib.pyplot as plt



# city_path = "../cities/san_francisco/"
# scenario = "Scenario_Set_1"
# if scenario[-1] == '2':
#     drop_off_percentage = [0.3]#[0.0, 0.1, 0.2, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]#[0.5]
#     drop_off_only_percentage = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# else:
#     drop_off_percentage = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]#[0.5]
#     drop_off_only_percentage = [0.0]

city_path = '../cities/san_francisco/'
scenario = 'Scenario_Set_3'
scenario_3_case = '3'
parking_supply = '0.2_parking'
if scenario[-1] == '2':
    drop_off_only_percentages = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
    drop_off_percentages = ['0.5'] #['0.5]
    reallocate_percentages = ['0.0']  # capacity increase of remaining off-street parking structures
    demand_reduced_by_parking_fee = None  # total travel demand reduced due to some 'imaginary' parking charge
elif scenario[-1] == '1':
    drop_off_only_percentages = ['0.0']
    drop_off_percentages = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
    reallocate_percentages = ['0.0']  # capacity increase of remaining off-street parking structures
    demand_reduced_by_parking_fee = None  # total travel demand reduced due to some 'imaginary' parking charge
elif scenario[-1] =='b':
    drop_off_only_percentages = ['0.0']  # percentage of on-street parking dedicated to drop-off only
    drop_off_percentages = ['0.5']  # percentage of drop-off trips
    reallocate_percentages = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']  # capacity increase of remaining off-street parking structures
    demand_reduced_by_parking_fee = None  # total travel demand reduced due to some 'imaginary' parking charge
elif scenario[-1] == '3':
    if scenario_3_case == '1':
        drop_off_only_percentages = ['0.0']  # percentage of on-street parking dedicated to drop-off only
        drop_off_percentages = ['0.0']  # percentage of drop-off trips
        reallocate_percentages = ['0.0']  # capacity increase of remaining off-street parking structures
        demand_reduced_by_parking_fee = 0.3  # total travel demand reduced due to some 'imaginary' parking charge
    elif scenario_3_case == '2':
        drop_off_only_percentages = ['0.5']  # percentage of on-street parking dedicated to drop-off only
        drop_off_percentages = ['0.5']  # percentage of drop-off trips
        reallocate_percentages = ['0.0']  # capacity increase of remaining off-street parking structures
        demand_reduced_by_parking_fee = 0.3  # total travel demand reduced due to some 'imaginary' parking charge
    elif scenario_3_case == '3':
        drop_off_only_percentages = ['0.0']  # percentage of on-street parking dedicated to drop-off only
        drop_off_percentages = ['0.5']  # percentage of drop-off trips
        reallocate_percentages = ['0.3']  # capacity increase of remaining off-street parking structures
        demand_reduced_by_parking_fee = 0.3  # total travel demand reduced due to some 'imaginary' parking charge

for i in drop_off_only_percentages:
    for j in drop_off_percentages:
        for k in reallocate_percentages:
            if scenario[-1] == '2':
                command = "python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py \
                            -n " + city_path + "san_francisco.net.xml -m occupancy,occupancy \
                            -i " + city_path + scenario + "/results/" + parking_supply + "/" + str(j) + "_drop-off_run2/edgedata_traffic_" + str(j) + "_drop-off_" + str(i) + "_drop-off_only.xml,"\
                                 + city_path + scenario + "/results/" + parking_supply + "/" + str(j) + "_drop-off_run2/edgedata_traffic_" + str(j) + "_drop-off_" + str(i) + "_drop-off_only.xml \
                            -v --min-color-value 0 --max-color-value 1.0 \
                            --colormap '#0:#00c000,.25:#408040,.5:#808080,.75:#804040,1:#c00000' \
                            -o " + city_path + scenario + "/plots/" + str(j) + "_drop-off/occupancy_" + str(i) + "_drop-off_only.png \
                            --title '" + str (100 * float(i)) + "% curbside parking \n dedicated to drop-off/pick-up traffic' --xlim 500,4500 --xlabel '[m]' --ylabel '[m]'\
                            "
            elif scenario[-1] == '1':
                command = "python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py \
                            -n " + city_path + "san_francisco.net.xml -m occupancy,occupancy \
                            -i " + city_path + scenario + "/results/" + parking_supply + "/edgedata_traffic_" + str(j) + "_drop-off.xml," \
                                 + city_path + scenario + "/results/" + parking_supply + "/edgedata_traffic_" + str(j) + "_drop-off.xml \
                            -v --min-color-value 0 --max-color-value 1.0 \
                            --colormap '#0:#00c000,.25:#408040,.5:#808080,.75:#804040,1:#c00000' \
                            -o " + city_path + scenario + "/plots/" + parking_supply + "/occupancy_" + str(j) + "_drop-off.png \
                            --title '" + str(100 * float(j)) + "% drop-off/pick-up traffic' --xlim 500,4500 --xlabel '[m]' --ylabel '[m]'"
            elif scenario[-1] == 'b':
                command = "python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py \
                            -n " + city_path + "san_francisco.net.xml -m occupancy,occupancy \
                            -i " + city_path + scenario + "/results/" + parking_supply + "/edgedata_traffic_" + str(j) + "_drop-off_" + str(k) + "_reallocation.xml," \
                                 + city_path + scenario + "/results/" + parking_supply + "/edgedata_traffic_" + str(j) + "_drop-off_" + str(k) + "_reallocation.xml \
                            -v --min-color-value 0 --max-color-value 1.0 \
                            --colormap '#0:#00c000,.25:#408040,.5:#808080,.75:#804040,1:#c00000' \
                            -o " + city_path + scenario + "/plots/" + parking_supply + "/occupancy_" + str(k) + "_reallocation.png \
                            --title '" + str(100 * float(k)) + "% off-street parking reallocation' --xlim 500,4500 --xlabel '[m]' --ylabel '[m]'"
            elif scenario[-1] == '3':
                if scenario_3_case == '3':
                    scenario_3_case_dir = scenario_3_case + '/' + parking_supply
                else:
                    scenario_3_case_dir = scenario_3_case
                command = "python3 ~/Desktop/VENTOS_all/sumo/tools/visualization/plot_net_dump.py \
                            -n " + city_path + "san_francisco.net.xml -m occupancy,occupancy \
                            -i " + city_path + scenario + "/results/case_" + scenario_3_case_dir + "/edgedata_traffic.xml," \
                                 + city_path + scenario + "/results/case_" + scenario_3_case_dir + "/edgedata_traffic.xml \
                            -v --min-color-value 0 --max-color-value 1.0 \
                            --colormap '#0:#00c000,.25:#408040,.5:#808080,.75:#804040,1:#c00000' \
                            -o " + city_path + scenario + "/plots/case_" + scenario_3_case + "/occupancy_" + str(k) + "_reallocation.png \
                            --xlim 500,4500 --xlabel '[m]' --ylabel '[m]'"
            os.system(command)
#