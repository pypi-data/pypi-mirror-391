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

```{code-cell} ipython3
import pandas as pd
```

```{code-cell} ipython3
NUMBERS = [f"{i:02d}" for i in range (1, 11)]
```

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
    df['relay'] = i
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

```{code-cell} ipython3
resampled = complete.groupby('relay').resample('15min').mean().reset_index()
resampled
```

```{code-cell} ipython3
%%timeit
resampled.to_json()
```

```{code-cell} ipython3

```
