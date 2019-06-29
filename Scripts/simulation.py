import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "sumo"
sumoCmd = [sumoBinary, "-c", "../cities/san_francisco/san_francisco.sumo.cfg"]
city = 'san_francisco'
scenario_dir = 'Scenario_Set_1'

import traci

traci.start(["sumo", "-c", "../cities/san_francisco/Scenario_Set_2/san_francisco.sumo.cfg",
             "-r", "../cities/san_francisco/san_francisco.rou.xml,../cities/san_francisco/Scenario_Set_2/trip_0.01_with_0.5_drop-off_0.5_drop-off_only.xml"], label="sim1")
traci.start(["sumo", "-c", "../cities/san_francisco/Scenario_Set_2/san_francisco.sumo.cfg",
             "-r", "../cities/san_francisco/san_francisco.rou.xml,../cities/san_francisco/Scenario_Set_2/trip_0.01_with_0.5_drop-off_0.8_drop-off_only.xml"], label="sim2")
conn1 = traci.getConnection("sim1")
conn2 = traci.getConnection("sim2")

step = 0
while step < 86400:
    # traci.simulationStep()
    conn1.simulationStep()  # run 1 step for sim1
    conn2.simulationStep()  # run 1 step for sim2
    step += 1

traci.close()