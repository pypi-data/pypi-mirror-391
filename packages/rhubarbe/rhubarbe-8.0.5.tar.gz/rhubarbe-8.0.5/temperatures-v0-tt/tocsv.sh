#!/bin/bash

for dat in "$@"; do
    csv=$(sed -e 's|\.dat|.csv|' <<< $dat)
    sed \
        -e 's|,|T|' \
        -e 's| |,|' \
    $dat > $csv
done
