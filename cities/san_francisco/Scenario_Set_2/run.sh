#!/bin/bash
trap "exit" INT TERM
trap "kill 0" EXIT
count=0
sample_rate=0.01
drop_off_percentage=0.5
for i in 0.0 0.5 1.0 #0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
	sumo -c san_francisco.sumo.cfg \
		-r ../san_francisco.rou.xml,trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$i"_drop-off_only.xml \
		--additional-files ../san_francisco.poly.xml,0.1_off_parking.add.xml,0.1_drop_off_parking.add.xml,edgedata_"$i"_drop-off_only.add.xml,../reroute_parking.xml \
		--stop-output results/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$i"_drop-off_only.xml \
	    --vehroute-output results/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$i"_drop-off_only.xml \
		--vehroutes.route-length true \
		--queue-output results/queue_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$i"_drop-off_only.xml \
		--summary results/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off_"$i"_drop-off_only.xml \
		&
	count=$((count + 1))
done
wait
echo "All $count simulations have completed!"
