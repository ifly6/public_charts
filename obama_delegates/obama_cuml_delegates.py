# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

dels = pd.read_html('https://www.nytimes.com/elections/2008/primaries/results/delegates/index.html',
                    match='American Samoa')[0]
dels.rename(columns={'Unnamed: 0': 'date', 'Unnamed: 1': 'state'}, inplace=True)
dels.drop(columns=['Unallocated', 'Future contests'], inplace=True)
dels.rename(columns=lambda s: s.replace(' ', '_').lower().strip(), inplace=True)

dels['date'] = dels['date'].ffill()


def parse_date(s):
    try:
        d = pd.to_datetime(s, format='%b. %d')
    except ValueError:
        try:
            d = pd.to_datetime(s, format='%b %d')
        except ValueError:
            d = pd.to_datetime(s, format='%B %d')

    d = d.replace(year=2008)
    return d


dels['date'] = dels['date'].apply(parse_date)
for c in ['barack_obama', 'hillary_rodham_clinton']:
    dels[c] = pd.to_numeric(dels[c], errors='coerce').fillna(0)

cumulative_dels = pd.concat([dels['date'], dels['barack_obama'].cumsum(),
                             dels['hillary_rodham_clinton'].cumsum()], axis=1)
cumulative_dels = cumulative_dels.groupby('date').max().reset_index()
cumulative_dels['obama_down_by'] = cumulative_dels.eval('hillary_rodham_clinton - barack_obama')

# pictures
f, a = plt.subplots(1, 1, figsize=(11, 8.5))
a.plot(cumulative_dels['date'], cumulative_dels['barack_obama'], label='Barack Obama')
a.plot(cumulative_dels['date'], cumulative_dels['hillary_rodham_clinton'], label='Hillary Clinton')
a.set_title('Cumulative Democratic delegates in 2008')
a.legend()

f1, a1 = plt.subplots(1, 1, figsize=(11, 8.5))
a1.plot(cumulative_dels['date'], cumulative_dels['obama_down_by'])
a1.set_title('Barack Obama, down by how many delegates?\n(Negative means Obama ahead)')
a1.plot(pd.date_range(cumulative_dels['date'].min().value, cumulative_dels['date'].max().value,
                      periods=50),
        np.repeat(0, 50),
        linestyle='--', color='gray')

f.savefig('delegates.png', bbox_inches='tight')
f1.savefig('obama.png', bbox_inches='tight')
cumulative_dels.to_csv('cumlt_dels.csv', index=False)
