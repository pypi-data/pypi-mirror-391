---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# convert old .dat files

see also

- `retrieve.sh`
- `tocsv.sh`

there's also `extract.sh` but that was only to produce small files for debugging

```{code-cell} ipython3
import pandas as pd
```

```{code-cell} ipython3
NUMBERS = [f"{i:02d}" for i in range (1, 11)]
```

## load

```{code-cell} ipython3
PREFIX = "relay"
# PREFIX = "extract"

def nth_file(i):
    return f"{PREFIX}-{i}.csv"
```

```{code-cell} ipython3
dfs = []
for i in NUMBERS: 
    df = pd.read_csv(nth_file(i), names=["timestamp", "temperature"])
    df['timestamp'] = pd.to_datetime(df.timestamp, format="ISO8601")
    df.set_index('timestamp', inplace=True)
    df['relay'] = f"relay-{i}"
    dfs.append(df)
```

```{code-cell} ipython3
# df = dfs[0]
# df
```

```{code-cell} ipython3
complete = pd.concat(dfs)
complete.shape
```

```{code-cell} ipython3
complete.head()
```

## resample on a 15 minute period

for each relay, do the mean() over a 15 minute period

```{code-cell} ipython3
resampled = complete.groupby('relay').resample('15min').mean()
resampled
```

## reorder timewise

```{code-cell} ipython3
reordered = (
    resampled
        .swaplevel()
        .sort_index()
        .reset_index())
reordered
```

```{code-cell} ipython3
with open("temperatures.csv", 'w') as writer:
    writer.write(
        reordered.to_csv(
            index=False,
            header=False,
            sep=',',
            date_format="%Y-%m-%dT%H:%M:%S",
            float_format="%.2f"
))
```

## reloading for the API

```{code-cell} ipython3
loaded = pd.read_csv(
    "temperatures.csv", names=["timestamp", "relay", "temperature"])
loaded['timestamp'] = pd.to_datetime(loaded['timestamp'], format="ISO8601")
loaded.set_index('timestamp', inplace=True)
loaded.head(2)
```

```{code-cell} ipython3
loaded.dtypes
```

```{code-cell} ipython3
#  duration resample_period

tests = [
    (None, None),
    ('1d', None),
    ('2w', '1h'),
    ('12w', '1d'),
]
```

```{code-cell} ipython3
from datetime import datetime as DateTime
from IPython.display import display

def filter(df, duration, resample_period):
    if duration is not None:
        duration = pd.Timedelta(duration)
        # print(type(duration))
        time_threshold = pd.Timestamp.now() - duration
        df = df[df.index >= time_threshold]
    if resample_period is not None:
        # resample already has string builtin conversion
        df = df.groupby('relay').resample(resample_period).mean()
    return df

for (d, p) in tests:
    print(f"duration={d} and period={p}")
    filtered = filter(loaded, d, p)
    print(filtered.shape)
    display(filtered)
```
