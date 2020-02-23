from lxml import etree, objectify
import pandas as pd
import numpy as np
from math import ceil
import matplotlib.pyplot as plt

def getVMT_sep(xmlfile):
    vmt_on, vmt_off, vmt_drop_off = 0, 0, 0
    num_on, num_off, num_drop_off = 0, 0, 0
    routes = etree.parse(xmlfile).getroot()

    for veh in routes:
        trip_length = float(veh.attrib['routeLength'])
        if veh.attrib['type'] == 'on':
            vmt_on += trip_length
            num_on += 1
        elif veh.attrib['type'] == 'off':
            vmt_off += trip_length
            num_off += 1
        else:
            vmt_drop_off += trip_length
            num_drop_off += 1
    print(num_on, num_off, num_drop_off)
    if num_drop_off == 0:
        if num_on != 0:
            return  vmt_on/1000, vmt_on/1000/num_on, vmt_off/1000, vmt_off/1000/num_off, vmt_drop_off/1000, 0
        if num_on == 0:
            return vmt_on / 1000, 0, vmt_off / 1000, vmt_off / 1000 / num_off, vmt_drop_off / 1000, 0
    elif num_on == 0:
        return  vmt_on/1000, 0, vmt_off/1000, vmt_off/1000/num_off, vmt_drop_off/1000,  vmt_drop_off/1000/num_drop_off
    else:
        return vmt_on/1000, vmt_on/1000/num_on, vmt_off/1000, vmt_off/1000/num_off, vmt_drop_off/1000, vmt_drop_off/1000/num_drop_off

def getVMT(xmlfile):
    vmt = 0
    empty_vmt = 0
    routes = etree.parse(xmlfile).getroot()

    # print('total vehicle: {}'.format(len(routes)))

    for veh in routes:
        trip_length = float(veh.attrib['routeLength'])
        vmt += trip_length
        if veh.attrib['type'] == 'drop-off':
            empty_vmt += trip_length/2

    return vmt/1000, vmt/1000/len(routes), empty_vmt/1000, empty_vmt/1000/len(routes)

def plotVMT_sep(scenerio):
    vmts_on, ave_vmts_on =np.zeros((10,11)),np.zeros((10,11))
    vmts_off, ave_vmts_off = np.zeros((10, 11)), np.zeros((10, 11))
    vmts_drop_off, ave_vmts_drop_off = np.zeros((10, 11)), np.zeros((10, 11))

    for l,j in enumerate(drop_off_percentages):
        for m,i in enumerate(drop_off_only_percentages):
            if scenerio[-1] == '2':
                RUNOUTS = np.array([getVMT_sep(path + scenerio +"/results/run_1/" + j +"_drop-off_run" + str(k) + "/vehroute_0.01_with_" + j
                                           + "_drop-off_" + i+ "_drop-off_only.xml") for k in range(1,3)])
                vmts_on[l,m]=np.mean(RUNOUTS,axis=0)[0]
                ave_vmts_on[l,m]=np.mean(RUNOUTS,axis=0)[1]
                vmts_off[l, m] = np.mean(RUNOUTS, axis=0)[2]
                ave_vmts_off[l, m] = np.mean(RUNOUTS, axis=0)[3]
                vmts_drop_off[l, m] = np.mean(RUNOUTS, axis=0)[4]
                ave_vmts_drop_off[l, m] = np.mean(RUNOUTS, axis=0)[5]
            elif scenerio[-1] == '1':
                vmts_on.append(getVMT(
                    path + scenerio + "/results/run1/"  + "vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml")[
                                0])
                ave_vmts_on.append(getVMT(
                    path + scenerio + "/results/run1/" + "vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml")[
                                    1])
    Plot(vmts_on,ave_vmts_on)
    Plot(vmts_off, ave_vmts_off)
    Plot(vmts_drop_off, ave_vmts_drop_off)

def plotVMT(scenerio):
    if scenario[-1] == 'b':
        vmts, ave_vmts = np.zeros((1, 10)), np.zeros((1, 10))
        empty_vmts, ave_empty_vmts = np.zeros((1, 10)), np.zeros((1, 10))
    else:
        vmts, ave_vmts = np.zeros((1,11)),np.zeros((1,11))
        empty_vmts, ave_empty_vmts = np.zeros((1, 11)), np.zeros((1, 11))

    for l,j in enumerate(drop_off_percentages):
        for m,i in enumerate(drop_off_only_percentages):
            for n, k in enumerate(reallocate_percentages):
                if scenerio[-1] == '2':
                    # RUNOUTS = np.array([getVMT(path + scenerio +"/results/run_1/" + j +"_drop-off_run" + str(k) + "/vehroute_0.01_with_" + j
                    #                            + "_drop-off_" + i+ "_drop-off_only.xml") for k in range(1,3)])
                    RUNOUTS = np.array([getVMT(
                        path + scenerio + "/results/" + parking_supply + "/" + j + "_drop-off_run" + str(k) + "/vehroute_0.01_with_" + j
                        + "_drop-off_" + i + "_drop-off_only.xml") for k in range(1, 11)])
                    vmts[l, m]=np.mean(RUNOUTS, axis=0)[0]
                    ave_vmts[l, m]=np.mean(RUNOUTS, axis=0)[1]
                    empty_vmts[l, m] = np.mean(RUNOUTS, axis=0)[2]
                    ave_empty_vmts[l, m] = np.mean(RUNOUTS, axis=0)[3]

                elif scenario[-1] == 'b':
                    vmts[m, n] = getVMT(
                        path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only_" + k + "_reallocation.xml")[
                        0]
                    ave_vmts[m, n] = getVMT(
                        path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only_" + k + "_reallocation.xml")[
                        1]
                    empty_vmts[m, n] = getVMT(
                        path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only_" + k + "_reallocation.xml")[
                        2]
                    ave_empty_vmts[m, n] = getVMT(
                        path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only_" + k + "_reallocation.xml")[
                        3]
                elif scenario[-1] == '3':
                    if scenario_3_case == '3':
                        file_path = path + scenerio + "/results/case_" + scenario_3_case + '/' + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml"
                    else:
                        file_path = path + scenerio + "/results/case_" + scenario_3_case + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml"
                    vmts[m, l] = getVMT(file_path)[0]
                    ave_vmts[m, l] = getVMT(file_path)[1]
                    empty_vmts[m, l] = getVMT(file_path)[2]
                    ave_empty_vmts[m, l] = getVMT(file_path)[3]
                elif scenerio[-1] == '1':
                    vmts[m, l] = getVMT(
                        path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml")[0]
                    ave_vmts[m, l] = getVMT(path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml")[1]
                    empty_vmts[m, l] = getVMT(path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml")[2]
                    ave_empty_vmts[m, l] = getVMT(path + scenerio + "/results/" + parking_supply + "/vehroute_0.01_with_" + j + "_drop-off_" + i + "_drop-off_only.xml")[3]
    print("VMTs: ", vmts)
    print("ave_vmts: ", ave_vmts)
    print("Empty VMTs: ", empty_vmts)
    print("ave_empty_vmts: ", ave_empty_vmts)

    # Plot_4(vmts, ave_vmts, empty_vmts, ave_empty_vmts)
    if scenario[-1] == '2':
        Plot(ave_vmts[:, [0, 2, 4, 6, 8, 9]], ave_empty_vmts[:, [0, 2, 4, 6, 8, 9]])
    elif scenario[-1] == 'b':
        Plot(vmts[:, [0, 2, 4, 6, 8]], empty_vmts[:, [0, 2, 4, 6, 8]])
    elif scenario[-1] == '1':
        Plot(ave_vmts, ave_empty_vmts)

    df = pd.DataFrame(map(list, zip(*[vmts[0], empty_vmts[0], ave_vmts[0], ave_empty_vmts[0]])),
                      columns=['vmt', 'empty vmt', 'ave vmt', 'ave empty vmt'])
    print(df)

    df.to_excel(path + scenario + '/results/vmt_results.xlsx')

import numpy.polynomial.polynomial as poly
from numpy.polynomial import Polynomial

def Plot_4(vmts, ave_vmts, empty_vmts, ave_empty_vmts):
    fig, ax1 = plt.subplots(figsize=(6,4))
    ax2 = ax1.twinx()

    for i in range(vmts.shape[0]):
        if scenario[-1] == '2':
            p = Polynomial.fit(range(0, 100, 10), vmts[i, :-1], 2)
            ax1.plot(*p.linspace(), color='blue', linewidth=4, label='polyfit')
            ax1.plot(range(0, 100, 10), vmts[i,:-1], 'k*--', label='VMT' )
            ax1.plot(range(0, 100, 10), empty_vmts[i,:-1], 'r*--', label='Empty VMT')
            ax2.plot(range(0, 100, 10), ave_vmts[i,:-1], color='gray', marker='^', label='Ave VMT' )
            ax2.plot(range(0, 100, 10), ave_empty_vmts[i,:-1], color='red', marker='^', label='Ave empty VMT')
            ax1.plot([100], vmts[i, -1], 'k*')
            ax2.plot([100], ave_vmts[i, -1], color='gray', marker='^')
        else:
            ax1.plot(range(0, 110, 10), vmts[i, :], 'k*--', label='VMT')
            ax1.plot(range(0, 110, 10), empty_vmts[i, :], 'r*--', label='Empty VMT')
            ax2.plot(range(0, 110, 10), ave_vmts[i, :], color='gray', marker='^', label='Ave VMT')
            ax2.plot(range(0, 110, 10), ave_empty_vmts[i, :], color='red', marker='^', label='Ave empty VMT')
        plt.subplots_adjust(left=0.15, bottom=0.15, right=0.9, top=0.92, wspace=0, hspace=0)
    if scenario[-1] == '2':
        ax1.set_xlabel('Percentage of curbside parking dedicated to drop-off/pick-up traffic (%)', fontsize=12)
    else:
        ax1.set_xlabel('Percentage of drop-off/pick-up traffic (%)',fontsize=12)
    ax1.set_ylabel('Total VMT(KM)',fontsize=12)
    ax2.set_ylabel('Average VMT(KM)',fontsize=12)
    ax1.grid(linestyle = '--')
    ax1.legend(loc=1)
    ax2.legend(loc=2)
    plt.savefig("../cities/san_francisco/"+ scenario+"/plots/VMT_vs_dropoff_percentage.png",dpi=800)
    plt.show()

def Plot(vmts, empty_vmts):
    fig, ax1 = plt.subplots(figsize=(6,4))
    ax2 = ax1.twinx()

    for i in range(vmts.shape[0]):
        if scenario[-1] == '2':
            p = Polynomial.fit([0, 20, 40, 60, 80, 90], vmts[i], 2)
            ax1.plot(*p.linspace(), color='blue', linewidth=4, label='polyfit')
            ax1.plot([0, 20, 40, 60, 80, 90], vmts[i], 'k*--', label='Ave VMT')
            #
            CO2 = [3.19, 3.22, 3.45, 3.62, 3.74, 5.15]
            # p = Polynomial.fit([0, 20, 40, 60, 80, 90], empty_vmts[i], 2)
            # ax1.plot(*p.linspace(), color='blue', linewidth=4, label='polyfit')
            # ax1.plot([0, 20, 40, 60, 80, 90], empty_vmts[i], 'r*--', label='Ave Empty VMT')
            ax2.plot([0, 20, 40, 60, 80, 90], CO2, color='green', marker='^', label=r'$CO_2$')
            # ax1.plot([100], vmts[i, -1], 'k*')
        elif scenario[-1] == '1':
            CO2 = [6, 4.47, 3.34, 2.69, 2.13, 2.23, 2.35, 2.48, 2.61, 2.72, 2.85]
            ax1.plot(range(0, 10*len(vmts[i]), 10), vmts[i, :], 'k^--', label='Ave VMT')
            ax1.plot(range(0, 10*len(vmts[i]), 10), empty_vmts[i, :], 'r^--', label='Ave Empty VMT')
            ax2.plot(range(0, 10*len(vmts[i]), 10), CO2, color='green', marker='^', label=r'$CO_2$')
        elif scenario[-1] == 'b':
            # ax1.plot(range(0, 10*len(vmts[i]), 10), vmts[i, :], 'k^--', label='VMT')
            # ax1.plot(range(0, 10*len(vmts[i]), 10), empty_vmts[i, :], 'r^--', label='Empty VMT')
            CO2 = [2.26, 2.32, 2.36, 3.07, 9.57]
            vmts[i, 1] = 111199.0833
            # ax1.plot([0, 20, 40, 60, 80], vmts[i, :], 'k^--', label='Ave VMT')
            # ax2.plot([0, 20, 40, 60, 80], CO2, color='green', marker='^', label=r'$CO_2$')
            ax1.plot([0, 20, 40, 60, 80], empty_vmts[i, :], 'r^--', label='Ave Empty VMT')
        plt.subplots_adjust(left=0.15, bottom=0.15, right=0.85, top=0.92, wspace=0, hspace=0)
    if scenario[-1] == '2':
        ax1.set_xlabel('Percentage of curbside parking dedicated to drop-off/pick-up traffic (%)', fontsize=12)
    elif scenario[-1] == 'b':
        ax1.set_xlabel('Percentage of reallocated off-street parking capacity (%)', fontsize=12)
    else:
        ax1.set_xlabel('Percentage of drop-off/pick-up traffic (%)',fontsize=12)
    ax1.set_ylabel('VMT(KM)',fontsize=12)
    ax2.set_ylabel(r'Ave $CO_2$ emission(Kg/veh)', fontsize=12)
    ax1.grid(linestyle = '--')
    ax1.legend(loc=1)
    ax2.legend(loc=2)
    plt.savefig("../cities/san_francisco/"+ scenario+"/plots/VMT_vs_dropoff_percentage.png",dpi=800)
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

#########################
## Travel time related ##
#########################
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
    return traveltime/3600, traveltime/len(routes)/60

def getEdgeTraffic(xmlfile):
    speeds, occupancies, waiting_times, count_v, count_o, count_w = 0, 0, 0, 0, 0, 0
    intervals = etree.parse(xmlfile).getroot()
    for interval in intervals:
        edges_traffic = interval.getchildren()
        for edge_traffic in edges_traffic:
            if 'speed' in edge_traffic.attrib:
                speed = float(edge_traffic.attrib['speed'])
                speeds += speed
                count_v += 1
            if 'occupancy' in edge_traffic.attrib:
                occupancy = float(edge_traffic.attrib['occupancy'])
                if occupancy > 0:
                    occupancies += occupancy
                    count_o += 1
            if 'waitingTime' in edge_traffic.attrib:
                waiting_time = float(edge_traffic.attrib['waitingTime'])
                waiting_times += waiting_time
                count_w += 1
    return speeds/count_v, occupancies/count_o, waiting_times/count_w/60

def plotTraveltime():
    tts, ave_tt = [], []
    ave_vs, ave_occs, ave_wts = [], [], []
    ave_vs_hourly = []
    if scenario[-1] == '2':
        runs = 10
    else:
        runs = 1
    for run in np.arange(runs):
        count_drop_off = 0
        for drop_off_percentage in drop_off_percentages:
            count_drop_off_only = 0
            for drop_off_only_percentage in drop_off_only_percentages:
                count_reallocation = 0
                for reallocate_percentage in reallocate_percentages:
                    if scenario[-1] == '1':
                        vehroute_xml = path + scenario + "/results/" + parking_supply + "/vehroute_0.01_with_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"
                        edgedata_traffic_xml = path + scenario + "/results/" + parking_supply + "/edgedata_traffic_" + drop_off_percentage + "_drop-off.xml"
                        count = count_drop_off
                        length = len(drop_off_percentages)
                    elif scenario[-1] == '2':
                        vehroute_xml = path + scenario + "/results/0.2_parking/" + drop_off_percentage + "_drop-off_run" + str(run+1) + "/vehroute_0.01_with_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"
                        edgedata_traffic_xml = path + scenario + "/results/0.2_parking/" + drop_off_percentage + "_drop-off_run" + str(run+1) + "/edgedata_traffic_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"
                        count = count_drop_off_only
                        length = len(drop_off_only_percentages)
                    elif scenario[-1] == '3':
                        if scenario_3_case == '1' or scenario_3_case == '2':
                            vehroute_xml = path + scenario + "/results/case_" + scenario_3_case + "/vehroute_0.01_with_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"
                            edgedata_traffic_xml = path + scenario + "/results/case_" + scenario_3_case + "/edgedata_traffic.xml"
                        elif scenario_3_case == '3':
                            vehroute_xml = path + scenario + "/results/case_" + scenario_3_case + "/" + parking_supply + "/vehroute_0.01_with_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"
                            edgedata_traffic_xml = path + scenario + "/results/case_" + scenario_3_case + "/" + parking_supply + "/edgedata_traffic.xml"
                        length = 1
                    elif scenario[-1] == 'b':
                        vehroute_xml = path + scenario + "/results/" + parking_supply + "/vehroute_0.01_with_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only_" + reallocate_percentage + "_reallocation.xml"
                        edgedata_traffic_xml = path + scenario + "/results/" + parking_supply + "/edgedata_traffic_" + drop_off_percentage + "_drop-off_" + reallocate_percentage + "_reallocation.xml"
                        count = count_reallocation
                        length = len(reallocate_percentages)

                    if len(tts) < length:
                        tts.append(getTraveltime(vehroute_xml)[0])
                        ave_tt.append(getTraveltime(vehroute_xml)[1])
                        ave_vs.append(getEdgeTraffic(edgedata_traffic_xml)[0])
                        ave_occs.append(getEdgeTraffic(edgedata_traffic_xml)[1])
                        ave_wts.append(getEdgeTraffic(edgedata_traffic_xml)[2])
                    else:
                        tts[count] += getTraveltime(vehroute_xml)[0]
                        ave_tt[count] += getTraveltime(vehroute_xml)[1]
                        ave_vs[count] += getEdgeTraffic(edgedata_traffic_xml)[0]
                        ave_occs[count] += getEdgeTraffic(edgedata_traffic_xml)[1]
                        ave_wts[count] += getEdgeTraffic(edgedata_traffic_xml)[2]

                    count_reallocation += 1
                count_drop_off_only += 1
            count_drop_off += 1
        print("Run {} done!".format(run))
    tts = [i/runs for i in tts]
    ave_tt = [i/runs for i in ave_tt]
    if scenario[-1] == 'b':
        tts[-1] = 14989.8
        ave_tt[-1] = 50.41
    ave_vs = [i/runs for i in ave_vs]
    ave_occs = [i/runs for i in ave_occs]
    ave_wts = [i/runs for i in ave_wts]

    # print("ttt: ", tts)
    # print("ave_tt: ", ave_tt)
    # print("Ave speed: ", ave_vs)
    # print("Ave occupancy: ", ave_occs)
    # print("Ave waiting time: ", ave_wts)

    df = pd.DataFrame(map(list, zip(*[tts, ave_tt, ave_vs, ave_occs, ave_wts])), columns=['tts', 'ave_tt', 'ave_vs', 'ave_occs', 'ave_wts'])
    print(df)


    df.to_excel(path + scenario + '/results/tt_results.xlsx')


    if scenario[-1] == '3':
        return
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(range(0, 10*len(tts), 10), tts, 'k*--', label='total travel time')
    ax2.plot(range(0, 10*len(tts), 10), ave_tt, color='gray', marker='^', label='Ave travel time')
    if scenario[-1] == '2':
        ax1.set_xlabel('Percentage of curbside parking dedicated to drop-off/pick-up traffic (%)')
    else:
        ax1.set_xlabel('Percentage of drop-off/pick-up traffic (%)')
    ax1.set_ylabel('Total travel time(hr)')
    ax2.set_ylabel('Average travel time(min)')
    ax1.grid(linestyle = '--')
    ax1.legend(loc=1)
    ax2.legend(loc=2)
    plt.savefig(path + scenario + "/plots/Traveltime_vs_dropoff_percentage.png", dpi=800)

    plt.show()

##########################
## edge traffic related ##
##########################
# todo: plot is not implemented yet
def plotEdgeTraffic():
    ave_vs, ave_occs, ave_wts = [], [], []
    for drop_off_percentage in drop_off_percentages:
        for drop_off_only_percentage in drop_off_only_percentages:
            if scenario[-1] == '1':
                edgedata_traffic_xml = path + scenario + "/results/edgedata_traffic_" + drop_off_percentage + "_drop-off.xml"

            elif scenario[-1] == '2':
                edgedata_traffic_xml = path + scenario + "/results/"+ drop_off_percentage + "_drop-off/edgedata_traffic_" + drop_off_percentage + "_drop-off_" + drop_off_only_percentage + "_drop-off_only.xml"

            elif scenario[-1] == '3':
                edgedata_traffic_xml = path + scenario + "/results/case_" + scenario_3_case + "/edgedata_traffic.xml"

            ave_vs.append(getEdgeTraffic(edgedata_traffic_xml)[0])
            ave_occs.append(getEdgeTraffic(edgedata_traffic_xml)[1])
            ave_wts.append(getEdgeTraffic(edgedata_traffic_xml)[2])
    print("Ave speed: ", ave_vs)
    print("Ave occupancy: ", ave_occs)
    print("Ave waiting time: ", ave_wts)


######################
## emission related ##
######################
def getEmission(xmlfile):
    factor = 1e6
    CO, CO2, NOx, PMx, HC, fuel = 0, 0, 0, 0, 0, 0
    intervals = etree.parse(xmlfile).getroot()
    for interval in intervals:
        edges_emission = interval.getchildren()
        for edge in edges_emission:
            CO += float(edge.attrib['CO_abs'])/factor
            CO2 += float(edge.attrib['CO2_abs'])/factor
            NOx += float(edge.attrib['NOx_abs'])/factor
            PMx += float(edge.attrib['PMx_abs'])/factor
            HC += float(edge.attrib['HC_abs'])/factor
            fuel += float(edge.attrib['fuel_abs'])/factor*1000

    return CO, CO2, NOx, PMx, HC, fuel

def getNumVeh(xml_file):
    routes = etree.parse(xml_file).getroot()
    return len(routes)

def plotEmission():
    Em = []
    ave_Em = []
    for j in drop_off_percentages:
        for i in drop_off_only_percentages:
            for k in reallocate_percentages:
                if scenario[-1] == '2':
                    num_veh = getNumVeh(path + scenario + "/results/" + parking_supply + "/" + j + "_drop-off_run2" + "/vehroute_0.01_with_" + j
                                    + "_drop-off_" + i + "_drop-off_only.xml")
                    tmp = getEmission(path + scenario + "/results/" + parking_supply + "/" + j + "_drop-off_run2" + "/edgedata_emission_" + j
                                    + "_drop-off_" + i + "_drop-off_only.xml")
                    ave_Em.append([x/num_veh for x in tmp])
                    Em.append(tmp)
                    index = drop_off_only_percentages
                elif scenario[-1] == '1':
                    num_veh = getNumVeh(
                        path + scenario + "/results/" + parking_supply + "/vehroute_0.01_with_" + j
                        + "_drop-off_" + i + "_drop-off_only.xml")
                    tmp = getEmission(path + scenario + "/results/" + parking_supply + "/edgedata_emission_" + j
                                    + "_drop-off.xml")
                    ave_Em.append([x/num_veh for x in tmp])
                    Em.append(tmp)
                    index = drop_off_percentages
                elif scenario[-1] == 'b':
                    num_veh = getNumVeh(path + scenario + "/results/" + parking_supply + "/vehroute_0.01_with_" + j
                                    + "_drop-off_" + i + "_drop-off_only_" + k + "_reallocation.xml")
                    tmp = getEmission(path + scenario + "/results/" + parking_supply + "/edgedata_emission_" + j
                                    + "_drop-off_" + k + "_reallocation.xml")
                    Em.append(tmp)
                    ave_Em.append([x/num_veh for x in tmp])
                    index = reallocate_percentages
                elif scenario[-1] == '3':
                    if scenario_3_case == '3':
                        scenario_3_case_dir = scenario_3_case + '/' + parking_supply
                    else:
                        scenario_3_case_dir = scenario_3_case
                    num_veh = getNumVeh(path + scenario + "/results/case_" + scenario_3_case_dir + "/vehroute_0.01_with_" + j
                                    + "_drop-off_" + i + "_drop-off_only.xml")
                    tmp = getEmission(path + scenario + "/results/case_" + scenario_3_case_dir + "/edgedata_emission.xml")
                    ave_Em.append([x/num_veh for x in tmp])
                    Em.append(tmp)
                    index = reallocate_percentages

    Em = pd.DataFrame(Em, index=index)
    Em.columns=['CO(Kg)', 'CO2(Kg)', 'NOx(Kg)', 'PMx(Kg)', 'HC(Kg)', 'fuel(L)']
    Em.to_excel("../cities/san_francisco/"+ scenario+"/plots/emission.xlsx",index=True,float_format='%.2f')
    ave_Em = pd.DataFrame(ave_Em, index=index)
    ave_Em.columns=['Ave CO(Kg/veh)', 'Ave CO2(Kg/veh)', 'Ave NOx(Kg/veh)', 'Ave PMx(Kg/veh)', 'Ave HC(Kg/veh)', 'Ave fuel(L/veh)']
    ave_Em.to_excel("../cities/san_francisco/"+ scenario+"/plots/ave_emission.xlsx",index=True,float_format='%.2f')

    # COs, CO2s, NOxs, PMxs, HCs, fuels = [], [], [], [], [], []
    # for drop_off_only_percentage in drop_off_only_percentages:
    #     COs.append(getEmission(
    #         "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
    #                    0]/1e6)
    #     CO2s.append(getEmission(
    #         "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
    #                    1]/1e6)
    #     NOxs.append(getEmission(
    #         "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
    #                    2]/1e6)
    #     PMxs.append(getEmission(
    #         "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
    #                    3]/1e6)
    #     HCs.append(getEmission(
    #         "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
    #                    4]/1e6)
    #     fuels.append(getEmission(
    #         "../cities/san_francisco/Scenario_Set_2/results/edgedata_emission_" + drop_off_only_percentage + "_drop-off_only.xml")[
    #                    5]/1e6)
    # # plt.plot(COs)
    # plt.plot(CO2s)
    # plt.plot(NOxs)
    # plt.plot(PMxs)
    # plt.plot(HCs)
    # plt.plot(fuels)
    # plt.show()

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

# origin, destination = OD_count('../cities/san_francisco/Scenario_Set_1/trip_0.01_with_' + '1.0' + '_drop-off.xml')
# print(origin, origin.sum(),destination,destination.sum())

def getPeakHourSpeed(summary_xml):
    steps = etree.parse(summary_xml).getroot()
    vs = np.zeros(24)
    running = np.zeros(24)
    am_vs, pm_vs = 0, 0
    am_running, pm_running = 0, 0
    for step in steps:
        time = int(float(step.attrib['time']))
        running_step = int(float(step.attrib['running']))
        ave_vs = float(step.attrib['meanSpeed'])

        if ave_vs >= 0:
            if time >= 6*3600 and time < 10*3600:
                am_vs += running_step * ave_vs
                am_running += running_step
            elif time >= 15*3600 and time < 19*3600:
                pm_vs += running_step * ave_vs
                pm_running += running_step

    am_vs /= am_running
    pm_vs /= pm_running
    return [am_vs, pm_vs]

def getHourlySpeed(summary_xml):
    steps = etree.parse(summary_xml).getroot()
    vs = np.zeros(24)
    running = np.zeros(24)
    am_vs, pm_vs = 0, 0
    am_running, pm_running = 0, 0
    for step in steps:
        time = int(float(step.attrib['time']))
        running_step = int(float(step.attrib['running']))
        ave_vs = float(step.attrib['meanSpeed'])

        if ave_vs >= 0:
            vs[int(time/3600)] += running_step * ave_vs
            running[int(time/3600)] += running_step

    vs /= running
    return np.nan_to_num(vs)

def getSpeed():
    hours = [str(i+1) for i in np.arange(24)]
    result_path = '/home/huajun/Desktop/Nextcloud/2019-work/NCST_parking/cities/san_francisco/' + scenario + '/results/'
    vs_hourly = []
    vs_peak = []
    for drop_off_percentage in drop_off_percentages:
        for drop_off_only_percentage in drop_off_only_percentages:
            for reallocate_percentage in reallocate_percentages:
                if scenario[-1] == '2':
                    xml_file = result_path + parking_supply + '/' + drop_off_percentage + '_drop-off_run5/summary_0.01_with_' + drop_off_percentage + '_drop-off_' + drop_off_only_percentage + '_drop-off_only.xml'
                    index = drop_off_only_percentages
                elif scenario[-1] == 'b':
                    xml_file = result_path + parking_supply + '/summary_0.01_with_' + drop_off_percentage + '_drop-off_' + drop_off_only_percentage + '_drop-off_only_' + reallocate_percentage + '_reallocation.xml'
                    index = reallocate_percentages
                elif scenario[-1] == '1':
                    xml_file = result_path + parking_supply + '/summary_0.01_with_' + drop_off_percentage + '_drop-off_' + drop_off_only_percentage + '_drop-off_only.xml'
                    index = drop_off_percentages
                elif scenario[-1] == '3':
                    if scenario_3_case == '3':
                        xml_file = result_path + 'case_' + scenario_3_case + '/' + parking_supply + '/summary_0.01_with_' + drop_off_percentage + '_drop-off_' + drop_off_only_percentage + '_drop-off_only.xml'
                    else:
                        xml_file = result_path + 'case_' + scenario_3_case + '/summary_0.01_with_' + drop_off_percentage + '_drop-off_' + drop_off_only_percentage + '_drop-off_only.xml'
                    index = drop_off_percentages
                vs_peak.append(getPeakHourSpeed(xml_file))
                vs_hourly.append(getHourlySpeed(xml_file).tolist())

    vs_peak_pd = pd.DataFrame(vs_peak, columns=['am_peak(m/s)', 'pm_peak(m/s)'], index=index)
    vs_peak_pd.to_excel(result_path + 'peak_hour_vs.xlsx')

    vs_pd = pd.DataFrame(vs_hourly, columns=hours, index=index)
    vs_pd.to_excel(result_path + 'hourly_vs.xlsx')

#####################
#       Setup       #
#####################
path = '../cities/san_francisco/'
scenario = 'Scenario_Set_2'
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

plotEmission()
# plotQueue()
# emissions = plotEmission()
# print(['{:.2f}'.format(e) for e in emissions[2]])
# getSpeed()
# plotVMT(scenerio=scenario)
# plotTraveltime()
# plotEdgeTraffic()

