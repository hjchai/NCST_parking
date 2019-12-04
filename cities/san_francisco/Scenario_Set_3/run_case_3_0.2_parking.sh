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
        for reallocate_percentage in 0.3
        do
            for reduced_demand in 0.3
            do
                sumo -c san_francisco.sumo.cfg \
                    -r ../san_francisco.rou.xml,trips/trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation_"$reduced_demand"_reduced_demand.xml \
                    --additional-files ../san_francisco.poly.xml,parking/"$parking_supply_percentage"_off_parking.add.xml,parking/"$parking_supply_percentage"_drop_off_parking.add.xml,edge_dump_config/edgedata_case_3_0.2_parking.add.xml,rerouter/reroute_parking_"$drop_off_only_percentage"_drop-off_only_"$reallocate_percentage"_reallocation.xml \
                    --stop-output results/case_3/0.2_parking/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
                    --vehroute-output results/case_3/0.2_parking/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
                    --vehroutes.route-length true \
                    --summary results/case_3/0.2_parking/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$drop_off_only_percentage"_drop-off_only.xml \
                    &
                count=$((count + 1))
            done
        done
    done
done
wait
echo "All $count simulations have completed!"
