# hacky temperatures ala tt

## the conversion script

```bash
# to fetch the .dat files from the relay boxes
./fetch-to-csv.sh
# to produce `temperatures.csv`
python convert-nb.py
```

(there's also `extract.sh` but that was only to produce small files for debugging)

## on the relay boxes

```bash
root@relay-01:~# crontab -l
*/1 * * * * python3 /home/tester/plottemp/datagen.py && /home/tester/plottemp/plottemp.sh &> /tmp/log.plottemp.txt
```

### the crux of the matter 

is to call this binary here
```bash
/usr/bin/vcgencmd measure_temp
```

### old data

was stored in this file

`/home/tester/plottemp/tempdata.dat`

- every 1 minute
- stored in localtime
- there is a hiatus on 2025-10-26 between 02:00 and 03:00 (DST fall back) as we get 2 times 02:xx, which causes problems when converting to UTC - we use ambiguous='NaT' to avoid errors, which results in NaT values for that hour
