#!/bin/bash
trap "exit" INT TERM
trap "kill 0" EXIT
count=0
sample_rate=0.01
for drop_off_percentage in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
	sumo -c san_francisco.sumo.cfg \
		-r ../san_francisco.rou.xml,trip_"$sample_rate"_with_"$drop_off_percentage"_drop-off.xml \
		--additional-files ../san_francisco.poly.xml,off_parking.add.xml,drop_off_parking.add.xml,edgedata_"$drop_off_percentage"_drop-off.add.xml \
		--stop-output results/stops_"$sample_rate"_with_"$drop_off_percentage"_drop-off.xml \
	       	--vehroute-output results/vehroute_"$sample_rate"_with_"$drop_off_percentage"_drop-off.xml \
		--vehroutes.route-length true \
		--queue-output results/queue_"$sample_rate"_with_"$drop_off_percentage"_drop-off.xml \
		--summary results/summary_"$sample_rate"_with_"$drop_off_percentage"_drop-off.xml \
		&
	count=$((count + 1))
done
wait
echo "All $count simulations have completed!"
