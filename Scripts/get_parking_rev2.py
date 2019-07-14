from lxml import etree, objectify
import pandas as pd
import numpy as np
from math import ceil
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


def Read_Stop_file(xmlfile):
    parkingid = {}
    additional = etree.parse(xmlfile).getroot()

    ids = []
    types = []
    ends = []
    starts = []

    for parkingid in additional.getchildren():
        ids.append(parkingid.attrib['id'])
        types.append(parkingid.attrib['type'])
        ends.append(int(float(parkingid.attrib['ended'])))
        starts.append(int(float(parkingid.attrib['started'])))


    return pd.DataFrame(ids),pd.DataFrame(types),pd.DataFrame(ends),pd.DataFrame(starts)

def Read_vehroute_file(xmlfile):
    parkingid = {}
    additional = etree.parse(xmlfile).getroot()

    ids = []
    types = []
    starts = []
    durations = []
    child = {}
    duration = 0

    for parkingid in additional.getchildren():
        ids.append(parkingid.attrib['id'])
        types.append(parkingid.attrib['type'])
        starts.append(int(float(parkingid.attrib['arrival'])))
        has_stop = False
        for child in parkingid.getchildren():
            if child.tag is 'stop':
                duration = int(float(child.attrib['duration']))
                has_stop = True
            else:
                continue
        if has_stop:
            durations.append(duration)
        else:
            durations.append(0)


    return pd.DataFrame(ids),pd.DataFrame(types),pd.DataFrame(durations),pd.DataFrame(starts)

def Read_vehroute_file_nozero(xmlfile):
    parkingid = {}
    additional = etree.parse(xmlfile).getroot()

    ids = []
    types = []
    starts = []
    durations = []
    child = {}
    duration = 0

    for parkingid in additional.getchildren():
        has_stop = False
        for child in parkingid.getchildren():
            if child.tag == 'stop':
                duration = int(float(child.attrib['duration']))
                has_stop = True
            else:
                continue
        if has_stop:
            durations.append(duration)
            ids.append(parkingid.attrib['id'])
            types.append(parkingid.attrib['type'])
            starts.append(int(float(parkingid.attrib['arrival'])))


    return pd.DataFrame(ids),pd.DataFrame(types),pd.DataFrame(durations),pd.DataFrame(starts)


def hist1(df):
    ## get the occupacy via time for each type
    types = df['type'].values
    starts = df['start'].values
    ends = df['end'].values
    occ = np.zeros((96,3))
    for type, start, end in zip(types,starts,ends):
        start_ind = start//900
        end_ind = ceil(end/900)-1
        occ_ind = np.arange(start_ind,min(end_ind+1,96))
        i = 0*(type == 'on') + 1 * (type == 'off') + 2 *(type == 'drop-off')
        for j in occ_ind:
            occ[j,i] +=1
    return occ

def hist(df):
    ## get the occupacy via time for each type
    types = df['type'].values
    starts = df['start'].values
    #ends = df['end'].values
    durations = df['duration'].values
    occ = np.zeros((96,3))
    for type, start, duration in zip(types,starts,durations):
        start_ind = start//900
        end = start + duration
        end_ind = ceil(end/900)-1
        occ_ind = np.arange(start_ind,min(end_ind+1,96))
        i = 0*(type == 'on') + 1 * (type == 'off') + 2 *(type == 'drop-off')
        for j in occ_ind:
            occ[j,i] +=1
    return occ


def am_sum(list):
    sum = 0
    for i in np.arange(24,40,1):
        sum += list[i]
    return sum
def pm_sum(list):
    sum = 0
    for i in np.arange(60,76,1):
        sum += list[i]
    return sum
def s_hist_plot(list,path):
    occ = np.array(list)
    #print(occ.shape)
    X, Y = np.meshgrid(np.arange(0,24,0.25), np.arange(0,110,10))
    Z1 = occ[:,:,0]
    Z2 = occ[:,:,1]
    Z3 = occ[:,:,2]
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X,Y,Z1,cmap=cm.coolwarm)
    ax.set_xlabel('Time of day',fontsize=12)
    ax.set_ylabel('Drop-off Percentage (%)',fontsize=12)
    ax.set_zlabel('Occupancy',fontsize=12)
    ax.set_title('On street Occupancy',fontsize=12)
    plt.savefig(path + "on_occupancy_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(0,110,10),[am_sum(Z1[i])/16 for i in range(11)],label='AM Peak: 06:00-10:00')
    ax.plot(np.arange(0,110,10),[pm_sum(Z1[i])/16 for i in range(11)],label='PM Peak: 15:00-19:00')
    ax.set_xlabel('Drop-off Percentage (%)',fontsize=12)
    ax.set_ylabel('Occupancy',fontsize=12)
    plt.legend(prop = {'size':12})
    plt.savefig(path + "on_occupancy_peak_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z2, cmap=cm.coolwarm)
    ax.set_xlabel('Time of day',fontsize=12)
    ax.set_ylabel('Drop-off Percentage (%)',fontsize=12)
    ax.set_zlabel('Occupancy',fontsize=12)
    ax.set_title('Off street Occupancy',fontsize=12)
    plt.savefig(path + "off_occupancy_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(0, 110, 10), [am_sum(Z2[i]) / 16 for i in range(11)], label='AM Peak: 06:00-10:00')
    ax.plot(np.arange(0, 110, 10), [pm_sum(Z2[i]) / 16 for i in range(11)], label='PM Peak: 15:00-19:00')
    ax.set_xlabel('Drop-off Percentage (%)',fontsize=12)
    ax.set_ylabel('Occupancy',fontsize=12)
    plt.legend(prop={'size':12})
    plt.savefig( path + "off_occupancy_peak_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z3, cmap=cm.coolwarm)
    ax.set_xlabel('Time of day',fontsize=12)
    ax.set_ylabel('Drop-off Percentage (%)',fontsize=12)
    ax.set_zlabel('Occupancy',fontsize=12)
    ax.set_title('Drop-Off Occupancy',fontsize=12)
    plt.savefig(path + "drop_off_occupancy_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(0, 110, 10), [am_sum(Z3[i]) / 16 for i in range(11)], label='AM Peak: 06:00-10:00')
    ax.plot(np.arange(0, 110, 10), [pm_sum(Z3[i]) / 16 for i in range(11)], label='PM Peak: 15:00-19:00')
    ax.set_xlabel('Drop-off Percentage (%)',fontsize=12)
    ax.set_ylabel('Occupancy',fontsize=12)
    plt.legend(prop={'size':12})
    plt.savefig(path + "drop_off_occupancy_peak_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()


occupacy1 = []
occupacy = []
list = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
for l in list:
    df_id,df_type,df_end,df_starts = Read_Stop_file('../cities/san_francisco/Scenario_Set_2/results/0.5_drop-off/stops_0.01_with_0.5'  + '_drop-off_' + l +'_drop-off_only.xml')
    out1 = pd.concat([df_id, df_type, df_end, df_starts], axis=1)
    out1.columns = ['id', 'type', 'end', 'start']
    occupacy1.append(hist1(out1))

    # df_id,df_type,df_duration,df_starts = Read_vehroute_file_nozero('../cities/san_francisco/Scenario_Set_2/results/0.5_drop-off/vehroute_0.01_with_0.5' + '_drop-off_' + l +'_drop-off_only.xml')
    # out = pd.concat([df_id,df_type,df_duration,df_starts],axis=1)
    # out.columns = ['id','type','duration','start']
    #
    # #calculate occupancy
    # occupacy.append(hist(out))  #11 * (96 * 3)

path1 = "../cities/san_francisco/Scenario_Set_2/plots/by_stop/"
path = "../cities/san_francisco/Scenario_Set_2/plots/"

s_hist_plot(occupacy1,path1)
#s_hist_plot(occupacy,path)