#!/bin/bash
trap "exit" INT TERM
trap "kill 0" EXIT
count=0
sample_rate=0.01
drop_off_percentage=0.5
for i in 0 1 2 3 4 5 6 7 8 9 
do
	sumo -c san_francisco.sumo.cfg \
		-r ../san_francisco.rou.xml,trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off_0."$i"_drop-off_only.xml \
		--additional-files ../san_francisco.poly.xml,off_parking.add.xml,drop_off_parking.add.xml,edgedata_0."$i"_drop-off_only.add.xml \
		--stop-output results/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off_0."$i"_drop-off_only.xml \
	       	--vehroute-output results/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off_0."$i"_drop-off_only.xml \
		--vehroutes.route-length true \
		--queue-output results/queue_"$sample_rate"_with_"$drop_off_percentage"_drop-off_0."$i"_drop-off_only.xml \
		--summary results/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off_0."$i"_drop-off_only.xml \
		&
	count=$((count + 1))
done
wait
echo "All $count simulations have completed!"
