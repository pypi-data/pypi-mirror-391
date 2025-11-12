# hacky temperatures ala tt

## `relay_control`

forget about it, we'll do storage and acquisition on faraday as part of monitorrelays

## on the relay boxes

```bash
root@relay-01:~# crontab -l
*/1 * * * * python3 /home/tester/plottemp/datagen.py && /home/tester/plottemp/plottemp.sh &> /tmp/log.plottemp.txt
```

the crux of the matter is here
```bash
/usr/bin/vcgencmd measure_temp
```

### old data

/home/tester/plottemp/tempdata.dat
