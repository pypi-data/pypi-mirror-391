# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # convert old .dat files
#
# see also
#
# - `retrieve.sh` - to fetch the .dat files from the relay boxes
# - `tocsv.sh` - to convert them into csv
#
# there's also `extract.sh` but that was only to produce small files for debugging

# %%
import pandas as pd

# %%
NUMBERS = [f"{i:02d}" for i in range (1, 11)]

# %% [markdown]
# ## load

# %%
PREFIX = "relay"
# PREFIX = "extract"

def nth_file(i):
    return f"{PREFIX}-{i}.csv"


# %%
dfs = []
for i in NUMBERS: 
    df = pd.read_csv(nth_file(i), names=["timestamp", "temperature"])
    df['timestamp'] = (
        pd.to_datetime(df.timestamp, format="ISO8601")
            .dt.tz_localize("Europe/Paris", ambiguous='NaT')
            .dt.tz_convert("UTC")
    )
    # df['timestamp'] = df.timestamp.dt.tz_convert("UTC")
    df.set_index('timestamp', inplace=True)
    df['relay'] = f"relay-{i}"
    dfs.append(df)

# %%
complete = pd.concat(dfs)
complete.shape

# %%
complete.tail()

# %% [markdown]
# ## resample on a 15 minute period
#
# for each relay, do the mean() over a 15 minute period

# %%
resampled = complete.groupby('relay').resample('15min').mean()
resampled

# %% [markdown]
# ## reorder timewise

# %%
reordered = (
    resampled
        .swaplevel()
        .sort_index()
        .reset_index())
reordered

# %%
with open("temperatures.csv", 'w') as writer:
    writer.write(
        reordered.to_csv(
            index=False,
            header=False,
            sep=',',
            date_format="%Y-%m-%dT%H:%M:%SZ",
            float_format="%.2f"
))

# %% [markdown]
# ## reloading for the API
#
# this is just a sandbox code, scaffolding what's actually running in the fastAPI code  
# see `inventoryrelays.py` and specifically `load_past_data`

# %%
loaded = pd.read_csv(
    "temperatures.csv", names=["timestamp", "relay", "temperature"])
loaded['timestamp'] = (
    pd.to_datetime(loaded['timestamp'], format="ISO8601")
)
print(f"timestamp column is of dtype {loaded.timestamp.dtype}")
loaded.set_index('timestamp', inplace=True)
loaded.tail(2)

# %%
loaded.dtypes

# %%
#  duration resample_period

tests = [
    (None, None),
    ('1d', None),
    ('2w', '1h'),
    ('12w', '1d'),
]

tests = [ ('2w', '1h') ]

# %%
from datetime import datetime as DateTime
from IPython.display import display

def filter(df, duration, resample_period):
    if duration is not None:
        duration = pd.Timedelta(duration)
        # print(type(duration))
        time_threshold = pd.to_datetime(pd.Timestamp.utcnow()) - duration
        # print(f"{type(df.index)=}")
        df = df[df.index >= time_threshold]
    if resample_period is not None:
        # resample already has string builtin conversion
        df = df.groupby('relay').resample(resample_period).mean()
    return df

for (d, p) in tests:
    print(f"duration={d} and period={p}")
    filtered = filter(loaded, d, p)
    print(filtered.shape)
    display(filtered.tail(2))

# %% [markdown]
# ## time f... zones and f... DST

# %%
samples = [
    "2025-08-15T12:00:00",    # was utc +2
    "2025-11-01T12:00:00",    # was utc +1
    "2025-10-26T02:30:00",    # was both !
]

series = pd.Series(samples)
series

# %%
pd.to_datetime(series).dt.tz_localize("Europe/Paris", ambiguous='NaT')
