from lxml import etree, objectify
import pandas as pd
import numpy as np
from math import ceil
import matplotlib.pyplot as plt

def getVMT(xmlfile):
    vmt = 0
    routes = etree.parse(xmlfile).getroot()

    for veh in routes:
        trip_length = float(veh.attrib['routeLength'])
        vmt += trip_length
    return vmt/1000, vmt/len(routes)/1000

def plotVMT():
    vmts, ave_vmts = [], []
    for drop_off_percentage in drop_off_percentages:
        vmts.append(getVMT("../cities/san_francisco/Scenario_Set_1/results/vehroute_0.01_with_" + drop_off_percentage + "_drop-off.xml")[0])
        ave_vmts.append(getVMT("../cities/san_francisco/Scenario_Set_1/results/vehroute_0.01_with_" + drop_off_percentage + "_drop-off.xml")[1])
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(range(0, 110, 10), vmts, 'k*--', label='VMT')
    ax2.plot(range(0, 110, 10), ave_vmts, color='gray', marker='^', label='Ave VMT')
    ax1.set_xlabel('Dropoff percentage(%)')
    ax1.set_ylabel('Total VMT(KM)')
    ax2.set_ylabel('Average VMT(KM)')
    ax1.grid(linestyle = '--')
    ax1.legend(loc=1)
    ax2.legend(loc=2)
    plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/VMT_vs_dropoff_percentage.png")
    plt.show()

def getQueues(xmlfile):
    queue_time, queue_length = [], []
    queue = etree.parse(xmlfile).getroot()
    for data in queue:
        lanes = data.getchildren()[0]
        lane_list = lanes.getchildren()
        if lane_list is None:
            queue_length.append(0)
            queue_time.append(0)
        else:
            queue_time_tmp, queue_length_tmp = 0, 0
            for lane in lane_list:
                queue_time_tmp += float(lane.attrib['queueing_time'])/3600
                queue_length_tmp += float(lane.attrib['queueing_length'])/1000
            if queue_time == []:
                queue_length.append(queue_length_tmp)
                queue_time.append(queue_time_tmp)
            else:
                queue_length.append(queue_length[-1] + queue_length_tmp)
                queue_time.append(queue_time[-1] + queue_time_tmp)

    return queue_time, queue_length

def plotQueue():
    queue_times, queue_lengths = [], []
    rates = ['0.0', '0.5', '1.0']
    for drop_off_percentage in rates:
        queue_times.append(getQueues("../cities/san_francisco/Scenario_Set_1/results/queue_0.01_with_" + drop_off_percentage + "_drop-off.xml")[0])
        queue_lengths.append(getQueues("../cities/san_francisco/Scenario_Set_1/results/queue_0.01_with_" + drop_off_percentage + "_drop-off.xml")[1])
    for queue_time, rate in zip(queue_times, rates):
        plt.plot(range(len(queue_time)), queue_time, label=rate)
    plt.xlabel('Time of day')
    plt.ylabel('Cummulative queueing time(hr)')
    plt.xticks(range(0,93600,7200), range(0,26,2))
    plt.legend()
    plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/queueing_time_vs_rate.png")
    # plt.show()

    plt.figure()
    for queue_length, rate in zip(queue_lengths, rates):
        plt.plot(range(len(queue_length)), queue_length, label=rate)
    plt.xlabel('Time of day')
    plt.ylabel('Cummulative queueing length(KM)')
    plt.xticks(range(0,93600,7200), range(0,26,2))
    plt.legend()
    plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/queueing_length_vs_rate.png")
    plt.show()



def getTraveltime(xmlfile):
    traveltime = 0
    routes = etree.parse(xmlfile).getroot()
    for veh in routes:
        depart = float(veh.attrib['depart'])
        arrival = float(veh.attrib['arrival'])
        if len(veh.getchildren()) > 1:
            parking_duration = float(veh.getchildren()[1].attrib['duration'])
        else:
            parking_duration = 0
        tt = arrival - depart - parking_duration
        traveltime += tt
    return traveltime/3600, traveltime/len(routes)/3600

def plotTraveltime():
    tts, ave_tt = [], []
    for drop_off_percentage in drop_off_percentages:
        tts.append(getTraveltime("../cities/san_francisco/Scenario_Set_1/results/vehroute_0.01_with_" + drop_off_percentage + "_drop-off.xml")[0])
        ave_tt.append(getTraveltime("../cities/san_francisco/Scenario_Set_1/results/vehroute_0.01_with_" + drop_off_percentage + "_drop-off.xml")[1])
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(range(0, 110, 10), tts, 'k*--', label='total travel time')
    ax2.plot(range(0, 110, 10), ave_tt, color='gray', marker='^', label='Ave travel time')
    ax1.set_xlabel('Dropoff percentage(%)')
    ax1.set_ylabel('Total travel time(hr)')
    ax2.set_ylabel('Average travel time(hr)')
    ax1.grid(linestyle = '--')
    ax1.legend(loc=1)
    ax2.legend(loc=2)
    plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/Traveltime_vs_dropoff_percentage.png")
    plt.show()

def getEmission(xmlfile):
    CO, CO2, NOx, PMx, HC, fuel = 0, 0, 0, 0, 0, 0
    intervals = etree.parse(xmlfile).getroot()
    for interval in intervals:
        edges_emission = interval.getchildren()
        for edge in edges_emission:
            CO += float(edge.attrib['CO_abs'])
            CO2 += float(edge.attrib['CO2_abs'])
            NOx += float(edge.attrib['NOx_abs'])
            PMx += float(edge.attrib['PMx_abs'])
            HC += float(edge.attrib['HC_abs'])
            fuel += float(edge.attrib['fuel_abs'])

    return CO, CO2, NOx, PMx, HC, fuel

def plotEmission():
    COs, CO2s, NOxs, PMxs, HCs, fuels = [], [], [], [], [], []
    for drop_off_only_percentage in drop_off_only_percentages:
        COs.append(getEmission(
            "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
                       0]/1e6)
        CO2s.append(getEmission(
            "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
                       1]/1e6)
        NOxs.append(getEmission(
            "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
                       2]/1e6)
        PMxs.append(getEmission(
            "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
                       3]/1e6)
        HCs.append(getEmission(
            "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
                       4]/1e6)
        fuels.append(getEmission(
            "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
                       5]/1e6)
    # plt.plot(COs)
    # plt.plot(CO2s)
    # plt.plot(NOxs)
    # plt.plot(PMxs)
    # plt.plot(HCs)
    # plt.plot(fuels)
    # plt.show()
    return COs, CO2s, NOxs, PMxs, HCs, fuels

drop_off_only_percentages = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
drop_off_percentages = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']

# plotVMT()
# plotQueue()
# plotTraveltime()
# emissions = plotEmission()
# print(['{:.2f}'.format(e) for e in emissions[2]])

######
def Trip_count(xmlfile,t1=6,t2=10,t3=15,t4=19):
    parkingid = {}
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        additional = etree.parse(xmlfile).getroot()

        departs = []

        for parkingid in additional.getchildren():
            departs.append(int(parkingid.attrib['depart']))
        count = np.zeros(5)
        for depart in departs:
            if depart < t1 * 3600:
                count[0] +=1
            elif depart < t2 *3600:
                count[1] +=1
            elif depart < t3 *3600:
                count[2] +=1
            elif depart < t4 *3600:
                count[3] +=1
            else:
                count[4] +=1

    return count


# count = Trip_count('../cities/san_francisco/Scenario_Set_1/trip_0.01_with_' + '0.0' + '_drop-off.xml')
# print(count,count.sum(),count/count.sum())

def OD_count(xmlfile, ODs=45):
    from_tazs = np.zeros(ODs)
    to_tazs = np.zeros((ODs))
    routes = etree.parse(xmlfile).getroot()
    sum = 0
    for trip in routes.getchildren():
        from_taz = trip.attrib['from_taz']
        to_taz = trip.attrib['to_taz']
        if from_taz != '':
            from_tazs[int(from_taz)] += 1
        if to_taz != '':
            to_tazs[int(to_taz)] += 1
        if trip.attrib['trip_type'] == 'drop-off':
            sum +=1
    print(sum)
    return from_tazs, to_tazs

origin, destination = OD_count('../cities/san_francisco/Scenario_Set_1/trip_0.01_with_' + '1.0' + '_drop-off.xml')
print(origin, origin.sum(),destination,destination.sum())
