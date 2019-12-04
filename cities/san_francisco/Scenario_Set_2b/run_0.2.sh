#!/bin/bash
trap "exit" INT TERM
trap "kill 0" EXIT
count=0
sample_rate=0.01
parking_supply_percentage=0.2
for drop_off_percentage in 0.5
do
    for drop_off_only_percentage in 0.0
    do
        for reallocate_percentage in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9
        do
            sumo -c san_francisco.sumo.cfg \
                -r ../san_francisco.rou.xml,trips/trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.xml \
                --additional-files ../san_francisco.poly.xml,parking/"$parking_supply_percentage"_off_parking_"$reallocate_percentage"_reallocation.add.xml,parking/"$parking_supply_percentage"_drop_off_parking.add.xml,edge_dump_config/0.2_parking/edgedata_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.add.xml,rerouter/reroute_parking_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.xml \
                --stop-output results/0.2_parking/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.xml \
                --vehroute-output results/0.2_parking/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.xml \
                --vehroutes.route-length true \
                --summary results/0.2_parking/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.xml \
                &
            count=$((count + 1))
        done
    done
done
wait
echo "All $count simulations have completed!"
