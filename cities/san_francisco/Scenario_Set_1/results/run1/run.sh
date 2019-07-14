#!/bin/bash
trap "exit" INT TERM
trap "kill 0" EXIT
count=0
sample_rate=0.01
parking_supply_percentage=0.2
for drop_off_percentage in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
    for drop_off_only_percentage in 0.0 #0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
    do
        sumo -c san_francisco.sumo.cfg \
            -r ../san_francisco.rou.xml,trips/trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
            --additional-files ../san_francisco.poly.xml,parking/0.2_off_parking.add.xml,parking/0.2_drop_off_parking.add.xml,edge_dump_config/edgedata_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.add.xml,rerouter/reroute_parking_"$drop_off_only_percentage"_drop-off_only.xml \
            --stop-output results/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
            --vehroute-output results/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
            --vehroutes.route-length true \
            --summary results/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
            &
        count=$((count + 1))
    done
done
wait
echo "All $count simulations have completed!"

#--queue-output results/"$drop_off_percentage"_drop-off/queue_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
