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



def parking_cost(df,on_rate=1,off_rate=4):
    types = df['type'].values
    durations = df['duration'].values
    costs = []
    for type,duration in zip(types,durations):
        if type == 'on':
            cost = ceil(duration/900) * on_rate
        elif type == 'off':
            cost = min(ceil(duration/3600) * off_rate,24)
        else:
            cost = 0

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

def plot_bar(df):
    on = df['on'].values
    off = df['off'].values
    drop_off = df['drop-off'].values
    ymax = max(on+off+drop_off)
    ind =df.index
    p1 = plt.bar(ind,on)
    p2 = plt.bar(ind,off,bottom=on)
    p3 = plt.bar(ind,drop_off,bottom=on+off)
    plt.ylabel('revenue($)')
    plt.legend((p1[0],p2[0],p3[0]),('on','off','drop-off'))
    plt.xticks(ind,['0','10','20','30','40','50','60','70','80','90','100'])
    plt.yticks(np.arange(0, ymax*1.1, 25000))
    plt.xlabel('Drop-off percentage(%)')
    # plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/rev_with_2dollar_drop_off.png")
    plt.savefig("../cities/san_francisco/Scenario_Set_1/plots/rev_with_0dollar_drop_off.png")
    plt.show()


def hist(df):
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




tot = pd.DataFrame(columns=['on','off','drop-off']) # create a　dataframe to store all the total cost
occupacy = []
list = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
for l in list:
    df_id,df_type,df_end,df_durations = Parkingtime('/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_1/trip_0.01_with_' + l + '_drop-off.xml')
    out = pd.concat([df_id,df_type,df_end,df_durations],axis=1)
    out.columns = ['id','type','end','duration']
    ## calculate cost
    out_cost = parking_cost(out)

    on,off,drop = total_cost(out_cost)
    newrow = {'on':on,'off':off,'drop-off':drop}
    tot = tot.append(newrow,ignore_index=True)

    ## calculate occupancy
    occupacy.append(hist(out))

# print(tot)
# plot_bar(tot)
hist_plot(occupacy)