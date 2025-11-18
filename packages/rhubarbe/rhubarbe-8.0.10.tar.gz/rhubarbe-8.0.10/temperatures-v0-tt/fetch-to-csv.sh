#!/bin/bash

for i in $(seq -w 1 10); do
    relay=relay-${i}
    dat="${relay}.dat"
    rsync -ai $relay:/home/tester/plottemp/tempdata.dat $dat
    csv=$(sed -e 's|\.dat|.csv|' <<< $dat)
    sed \
        -e 's|,|T|' \
        -e 's| |,|' \
    $dat > $csv
done
echo "Data retrieval complete - output in relay-*.csv files."

echo "you can now run convert-nb.py to produce temperatures.csv"
exit 0
