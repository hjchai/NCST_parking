import os, sys
import traci
import numpy as np

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "sumo"
sumoCmd = [sumoBinary, "-c", "../cities/san_francisco/san_francisco.sumo.cfg"]

city = 'san_francisco'
scenario = 'Scenario_Set_3'
sample_rate = '0.01'
drop_off_percentage = '0.5'
drop_off_only_percentage = '0.0'

city_path = '../cities/' + city
scenario_path = city_path + '/' + scenario
cfg_path = scenario_path + "/" + city + '.sumo.cfg'
rou_path = city_path + "/" + city + '.rou.xml'
trip_path = scenario_path + "/trips/trip_" + sample_rate + "_with_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"
poly_path = city_path + "/" + city + ".poly.xml"
off_parking_path = scenario_path + "/parking/off_parking.add.xml"
drop_off_parking_path = scenario_path + "/parking/drop_off_parking.add.xml"

conns = []
for i in np.arange(2):
    sim_id = "sim" + str(i)
    traci.start(["sumo", "-c", cfg_path,
             "-r", rou_path + "," + trip_path,
             "--additional-files", poly_path + "," + off_parking_path + "," + drop_off_parking_path], label=sim_id)
# traci.start(["sumo", "-c", "../cities/san_francisco/Scenario_Set_2/san_francisco.sumo.cfg",
#             "-r", "../cities/san_francisco/san_francisco.rou.xml,../cities/san_francisco/Scenario_Set_2/trip_0.01_with_0.5_drop-off_0.8_drop-off_only.xml"], label="sim2")
    conns.append(traci.getConnection(sim_id))
# conn2 = traci.getConnection("sim2")

step = 0
while step < 86400:
    # traci.simulationStep()
    for conn in conns:
        conn.simulationStep()  # run 1 step for sim1
    # conn2.simulationStep()  # run 1 step for sim2
    step += 1

traci.close()


# -r ../san_francisco.rou.xml,trips/trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
#             --additional-files ../san_francisco.poly.xml,parking/off_parking.add.xml,parking/drop_off_parking.add.xml,edge_dump_config/edgedata_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.add.xml,rerouter/reroute_parking_"$drop_off_only_percentage"_drop-off_only.xml \
#             --stop-output results/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
#             --vehroute-output results/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
#             --vehroutes.route-length true \
#             --summary results/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \