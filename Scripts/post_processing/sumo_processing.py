import matplotlib.pyplot as plt
from lxml import etree, objectify
import os, sys
import pandas as pd
import numpy as np

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import xml

def plot_queue_flow(queues, plot_target, smoothing_step):
    sim_time = int(queues[-1:]['data_timestep'])
    queue_length = []
    queue_time = []
    for t in range(sim_time):
        if plot_target is "all":
            queue_length.append(sum(queues.loc[queues['data_timestep'] == t]['lane_queueing_length']))
            queue_time.append(sum(queues.loc[queues['data_timestep'] == t]['lane_queueing_time']))
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    df = pd.DataFrame(list(zip(queue_length, queue_time)), columns=['queue_length', 'queue_time'])
    if smoothing_step > 1:
        df_smooth = df.groupby(np.arange(len(df)) // smoothing_step).mean()
    else:
        df_smooth = df
    ax1.plot(range(0, sim_time, smoothing_step), df_smooth['queue_length'], 'k+-', markersize=5, linewidth=1, label='Queueing Length')
    ax2.plot(range(0, sim_time, smoothing_step), df_smooth['queue_time'], 'r^-', markersize=5, linewidth=1, label='Queueing Time')
    ax1.set_xlabel('Simulation Time (s)')
    ax1.set_ylabel('Queueing Length (m)')
    ax2.set_ylabel('Queueing Time (s)')
    fig.legend()

def plot_simulation_summary(summary, attributes, smoothing_step):
    sim_time = len(summary)
    if smoothing_step >1:
        summary_smooth = summary.groupby(np.arange(len(summary)) // smoothing_step).mean()
    else:
        summary_smooth = summary
    f1 = plt.figure(1)
    for key in attributes[:4]:
        plt.plot(summary[key], label=key)
    plt.ylabel('Number of Vehicles (veh)')
    plt.xlabel('Simulation Time (s)')
    f1.legend()

    f2, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(range(0, sim_time, smoothing_step), summary_smooth["step_meanTravelTime"], 'k+-', markersize=5, linewidth=1, label="Mean Travel Time")
    ax2.plot(range(0, sim_time, smoothing_step), summary_smooth["step_meanSpeed"], 'r^-', markersize=5, linewidth=1, label="Mean Speed")
    ax1.set_xlabel("Simulation Time (s)")
    ax1.set_ylabel("Mean Travel Time (s)")
    ax2.set_ylabel("Mean Speed (m/s)")
    f2.legend()

def process_csv(input_csv):
    results = pd.read_csv(input_csv, sep=";")
    return results

def xml2csv(input_xml):
    xml.

if __name__ == "__main__":
    smoothing_step = 1
    oe = "-oe"
    # summary_csv = "C:\Users\chaih\Desktop\VENTOS\examples\\router\sumocfg\grid_4x4\summary" + oe +".csv"
    summary_csv = '/home/huajun/Desktop/NCST_parking/cities/fairfield/results/summary_0.csv'
    attributes = ["step_inserted", "step_running", "step_ended", "step_waiting", "step_meanTravelTime", "step_meanSpeed"]
    summaries = process_csv(summary_csv)
    plot_simulation_summary(summaries, attributes, smoothing_step)

    # queue_csv = "C:\Users\chaih\Desktop\VENTOS\examples\\router\sumocfg\grid_4x4\queue" + oe + ".csv"
    queue_csv = '/home/huajun/Desktop/NCST_parking/cities/fairfield/results/queue_0.csv'
    queues = process_csv(queue_csv)
    plot_queue_flow(queues, "all", smoothing_step)

    plt.show()