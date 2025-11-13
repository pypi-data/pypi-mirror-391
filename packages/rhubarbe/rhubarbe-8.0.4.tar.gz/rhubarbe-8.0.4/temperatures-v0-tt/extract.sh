#!/bin/sh

for i in $(seq -w 1 10); do
    relay=relay-${i}
    csv="${relay}.csv"
    tail -n 200 $csv > extract-${i}.csv
done
echo "Data extraction complete."
exit 0
