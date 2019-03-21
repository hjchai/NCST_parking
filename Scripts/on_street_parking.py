import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib

def extractEdgesROI(roi, net):
    top_left, top_right, bot_left, bot_right = roi
    print(top_left)

if __name__ == "__main__":
    network_file = "/home/huajun/Desktop/VENTOS_all/VENTOS/examples/router/sumocfg/sfpark/network.net.xml"
    roi = [1, 2, 3, 4]
    net = sumolib.net.readNet(network_file)
    extractEdgesROI(roi, net)
    print("Okay")