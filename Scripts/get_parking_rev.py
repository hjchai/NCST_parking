from lxml import etree, objectify
import pandas as pd
import numpy as np
from math import ceil
import matplotlib.pyplot as plt



def Parkingtime(xmlfile):
    parkingid = {}
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        additional = etree.parse(xmlfile).getroot()

        ids = []
        types = []
        departs = []
        durations = []
        stop = {}
        duration = 0
        for parkingid in additional.getchildren():
            ids.append(parkingid.attrib['id'])
            types.append(parkingid.attrib['trip_type'])
            departs.append(int(parkingid.attrib['depart']))

            for stop in parkingid.getchildren():
                if stop is None:
                    duration = 0
                else:
                    duration = int(stop.attrib['duration'])
            durations.append(duration)

    return pd.DataFrame(ids),pd.DataFrame(types),pd.DataFrame(departs),pd.DataFrame(durations)



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


# #Parkingtime('../../cities/san_francisco/Scenario_Set_1/trip_0.01_with_0.5_drop-off.xml')

tot = pd.DataFrame(columns=['on','off','drop-off']) # create a　dataframe to store all the total cost

for l in ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']:
    df_id,df_type,df_departs,df_durations = Parkingtime('/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_1/trip_0.01_with_' + l + '_drop-off.xml')
    out = pd.concat([df_id,df_type,df_departs,df_durations],axis=1)
    out.columns = ['id','type','depart','duration']

    out_cost = parking_cost(out)

    on,off,drop = total_cost(out_cost)
    newrow = {'on':on,'off':off,'drop-off':drop}
    tot = tot.append(newrow,ignore_index=True)

print(tot)
plot_bar(tot)