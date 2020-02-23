from lxml import etree, objectify
import pandas as pd
import numpy as np
from math import ceil
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


def Parkingtime(xmlfile):
    parkingid = {}
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        additional = etree.parse(xmlfile).getroot()

        ids = []
        types = []
        ends = []
        durations = []
        stop = {}
        duration = 0
        for parkingid in additional.getchildren():
            ids.append(parkingid.attrib['id'])
            types.append(parkingid.attrib['trip_type'])
            ends.append(int(parkingid.attrib['end']))

            for stop in parkingid.getchildren():
                if stop is None:
                    duration = 0
                else:
                    duration = int(stop.attrib['duration'])
            durations.append(duration)

    return pd.DataFrame(ids),pd.DataFrame(types),pd.DataFrame(ends),pd.DataFrame(durations)



def parking_cost(df,on_rate=1,off_rate=4,drop_cost = 0):
    types = df['type'].values
    durations = df['duration'].values
    costs = []
    for type,duration in zip(types,durations):
        if type == 'on':
            cost = ceil(duration/900) * on_rate
        elif type == 'off':
            cost = min(ceil(duration/3600) * off_rate,24)
        else:
            cost = drop_cost

        costs.append(cost)

    df_cost = pd.DataFrame(costs,columns=['Cost'])
    return pd.concat([df,df_cost],axis=1)


def total_cost(df):
    types = df['type'].values
    costs = df['Cost'].values
    drop_tot = 0
    on_tot = 0
    off_tot = 0
    for type,cost in zip(types,costs):
        if type == 'on':
            on_tot += cost
        elif type == 'off':
            off_tot += cost
        else:
            drop_tot += cost

    return on_tot,off_tot,drop_tot

def plot_bar(df, dropoff_count, path='Scenario_Set_1/plots/',drop_cost=0):
    on = df['on'].values
    off = df['off'].values
    drop_off = df['drop-off'].values
    ymax = max(on+off+drop_off)
    ind =df.index
    plt.figure(figsize=(8,6))
    p1 = plt.bar(ind,on)
    p2 = plt.bar(ind,off,bottom=on)
    p3 = plt.bar(ind,drop_off,bottom=on+off)
    plt.ylabel('Revenue($)', fontsize=16)
    plt.legend((p1[0],p2[0],p3[0]),('on-street','off-street','drop-off'),prop={'size':16})
    plt.xticks(ind,['0','10','20','30','40','50','60','70','80','90','100'])
    plt.yticks(np.arange(0, ymax*1.1, 25000))
    if path == 'Scenario_Set_1/plots/':
        plt.xlabel('Percentage of drop-off/pick-up traffic (%)', fontsize=16)
    else:
        plt.xlabel('Percentage of curbside parking dedicated to drop-off/pick-up traffic (%)', fontsize=16)
    # plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/rev_with_2dollar_drop_off.png")
    plt.savefig("../cities/san_francisco/"+path+"rev_with_"+str(drop_cost)+"dollar_drop_off.png")
    if path == 'Scenario_Set_1/plots/' and drop_cost == 0:
        plt.figure(figsize=(8, 6))
        plt.ylabel('Drop-off fee ($)', fontsize=16)
        plt.xlabel('Percentage of drop-off/pick-up traffic (%)', fontsize=16)
        drop_off_fees = [0]
        base_rev = on[0] + off[0] + drop_off[0]
        for on_, off_, drop_off_, dropoff_count_ in zip(on, off, drop_off, dropoff_count):
            if dropoff_count_ == 0:
                continue
            drop_off_fees.append((base_rev - on_ - off_)/dropoff_count_)
        plt.bar(ind, drop_off_fees)
        plt.xticks(ind, ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])
        plt.savefig("../cities/san_francisco/" + path + "drop_off_fees.png")
    plt.show()


def hist(df):
    ## get the occupacy via time for each type
    types = df['type'].values
    durations = df['duration'].values
    ends = df['end'].values
    occ = np.zeros((96,3))
    starts = ends-durations
    for type, start, end in zip(types,starts,ends):
        start_ind = start//900
        end_ind = ceil(end/900)-1
        occ_ind = np.arange(start_ind,min(end_ind+1,96))
        i = 0*(type == 'on')+ 1 * (type == 'off') + 2 *(type =='drop-off')
        for j in occ_ind:
            occ[j,i] +=1
    return occ


def hist_plot(list):
    occ = np.array(list)
    #print(occ.shape)
    X, Y = np.meshgrid(np.arange(0,24,0.25), np.arange(0,110,10))
    Z1 = occ[:,:,0]
    Z2 = occ[:,:,1]
    Z3 = occ[:,:,2]
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(221, projection='3d')
    ax.plot_surface(X,Y,Z1,cmap=cm.coolwarm)
    ax.set_xlabel('Time of day')
    ax.set_ylabel('Percentage (%)')
    ax.set_zlabel('Occupancy')
    ax.set_title('On street Occupancy')
    ax = fig.add_subplot(222, projection='3d')
    ax.plot_surface(X, Y, Z2, cmap=cm.coolwarm)
    ax.set_xlabel('Time of day')
    ax.set_ylabel('Percentage (%)')
    ax.set_zlabel('Occupancy')
    ax.set_title('Off street Occupancy')
    ax = fig.add_subplot(223, projection='3d')
    ax.plot_surface(X, Y, Z3, cmap=cm.coolwarm)
    ax.set_xlabel('Time of day')
    ax.set_ylabel('Percentage (%)')
    ax.set_zlabel('Occupancy')
    ax.set_title('Drop-Off Occupancy')
    plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/occupancy_vs_dropoff_percentage.png",bbox_inches='tight', dpi=1000)
    plt.show()

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

def s_hist_plot(list):
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
    ax.set_ylabel('Percentage of drop-off/pick-up traffic  (%)',fontsize=12)
    ax.set_zlabel('Occupancy',fontsize=12)
    ax.set_title('On street Occupancy',fontsize=12)
    plt.savefig("../cities/san_francisco/Scenario_Set_2/plots/on_occupancy_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(0,110,10),[am_sum(Z1[i])/16 for i in range(11)],label='AM Peak: 06:00-10:00')
    ax.plot(np.arange(0,110,10),[pm_sum(Z1[i])/16 for i in range(11)],label='PM Peak: 15:00-19:00')
    ax.set_xlabel('Percentage of drop-off/pick-up traffic  (%)',fontsize=12)
    ax.set_ylabel('Occupancy',fontsize=12)
    plt.legend(prop = {'size':12})
    plt.savefig("../cities/san_francisco/Scenario_Set_2/plots/on_occupancy_peak_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z2, cmap=cm.coolwarm)
    ax.set_xlabel('Time of day',fontsize=12)
    ax.set_ylabel('Percentage of drop-off/pick-up traffic  (%)',fontsize=12)
    ax.set_zlabel('Occupancy',fontsize=12)
    ax.set_title('Off street Occupancy',fontsize=12)
    plt.savefig("../cities/san_francisco/Scenario_Set_2/plots/off_occupancy_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(0, 110, 10), [am_sum(Z2[i]) / 16 for i in range(11)], label='AM Peak: 06:00-10:00')
    ax.plot(np.arange(0, 110, 10), [pm_sum(Z2[i]) / 16 for i in range(11)], label='PM Peak: 15:00-19:00')
    ax.set_xlabel('Percentage of drop-off/pick-up traffic  (%)',fontsize=12)
    ax.set_ylabel('Occupancy',fontsize=12)
    plt.legend(prop={'size':12})
    plt.savefig("../cities/san_francisco/Scenario_Set_2/plots/off_occupancy_peak_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z3, cmap=cm.coolwarm)
    ax.set_xlabel('Time of day',fontsize=12)
    ax.set_ylabel('Percentage of drop-off/pick-up traffic  (%)',fontsize=12)
    ax.set_zlabel('Occupancy',fontsize=12)
    ax.set_title('Drop-Off Occupancy',fontsize=12)
    plt.savefig("../cities/san_francisco/Scenario_Set_2/plots/drop_off_occupancy_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(0, 110, 10), [am_sum(Z3[i]) / 16 for i in range(11)], label='AM Peak: 06:00-10:00')
    ax.plot(np.arange(0, 110, 10), [pm_sum(Z3[i]) / 16 for i in range(11)], label='PM Peak: 15:00-19:00')
    ax.set_xlabel('Percentage of drop-off/pick-up traffic  (%)',fontsize=12)
    ax.set_ylabel('Occupancy',fontsize=12)
    plt.legend(prop={'size':12})
    plt.savefig("../cities/san_francisco/Scenario_Set_2/plots/drop_off_occupancy_peak_vs_dropoff_percentage.png", bbox_inches='tight',
                dpi=1000)
    plt.show()


tot = pd.DataFrame(columns=['on','off','drop-off']) # create a　dataframe to store all the total cost
dropoff_count = []
occupacy = []
list = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
drop_cost = 0
for l in list:
    df_id,df_type,df_end,df_durations = Parkingtime('../cities/san_francisco/Scenario_Set_1/trips/trip_0.01_with_' + l + '_drop-off_0.0_drop-off_only.xml')
    out = pd.concat([df_id,df_type,df_end,df_durations],axis=1)
    out.columns = ['id','type','end','duration']
    ## calculate cost
    out_cost = parking_cost(out, drop_cost=drop_cost)

    on,off,drop = total_cost(out_cost)
    newrow = {'on':on, 'off':off, 'drop-off':drop}
    tot = tot.append(newrow, ignore_index=True)

    dropoff_count.append(sum(df_type.iloc[:, 0].values == 'drop-off'))

    ## calculate occupancy
    #occupacy.append(hist(out))  #11 * (96 * 3)

print(tot)
plot_bar(tot, dropoff_count, drop_cost=drop_cost)

# tot = pd.DataFrame(columns=['on','off','drop-off']) # create a　dataframe to store all the total cost
# occupacy = []
# list = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
# for l in list:
#     df_id,df_type,df_end,df_durations = Parkingtime('/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_2/trips/trip_0.01_with_0.3'  + '_drop-off_' + l +'_drop-off_only.xml')
#     out = pd.concat([df_id,df_type,df_end,df_durations],axis=1)
#     out.columns = ['id','type','end','duration']
#     ## calculate cost
#     out_cost = parking_cost(out,drop_cost=2)
#
#     on,off,drop = total_cost(out_cost)
#     newrow = {'on':on,'off':off,'drop-off':drop}
#     tot = tot.append(newrow,ignore_index=True)
#
#     #calculate occupancy
#     #occupacy.append(hist(out))  #11 * (96 * 3)
#
# print(tot)
# plot_bar(tot,path='Scenario_Set_2/plots/0.3_drop-off/',drop_cost=2)
