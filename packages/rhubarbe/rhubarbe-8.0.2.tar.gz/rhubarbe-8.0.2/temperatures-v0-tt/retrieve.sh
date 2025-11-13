#!/bin/bash

for i in $(seq -w 1 10); do
    relay=relay-${i}
    dat="${relay}.dat"
    rsync -ai $relay:/home/tester/plottemp/tempdata.dat $dat
done
echo "Data retrieval complete."
exit 0
