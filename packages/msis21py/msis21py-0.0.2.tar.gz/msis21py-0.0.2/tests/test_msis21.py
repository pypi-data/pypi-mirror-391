# %%
from __future__ import annotations
from datetime import datetime, UTC
import matplotlib
from msis21py import NrlMsis21
import matplotlib.pyplot as plt
import numpy as np
# %%
usetex = False
if not usetex:
    # computer modern math text
    matplotlib.rcParams.update({'mathtext.fontset': 'cm'})

matplotlib.rc(
    'font', **{
        'family': 'serif',
        'serif': ['Times' if usetex else 'Times New Roman']
    }
)
matplotlib.rc('text', usetex=usetex)
# %%
MON = 12
msis21 = NrlMsis21()
date = time = datetime(2022, 3, 22, 18, 0).astimezone(UTC)
glat = 42.6
glon = -71.2
ds20 = msis21.evaluate(
    date, glat, glon, np.arange(60, 801, 5)
)
# %%
ig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=300)
tax = ax.twiny()
species = ['O', 'O2', 'N2', 'NO']
descs = ['O', 'O$_2$', 'N$_2$', 'NO']
# species = ['N+']
colors = ['r', 'g', 'b', 'm']
labels = []
lines = []
for spec, color, desc in zip(species, colors, descs):
    l21, = ds20[spec].plot(y='alt_km', ax=ax, color=color, lw=0.75)
    lines.extend([l21])
    labels.extend([desc])
ax.set_title('NRLMSIS-2.1')
l21, = ds20['Tn'].plot(y='alt_km', ax=tax, color='k', lw=0.75)
lines.extend([l21])
labels.extend(['${T_n}$'])
ax.set_title('NRLMSIS-2.1')
ax.set_xscale('log')
ax.set_xlabel('Number Density [cm$^{-3}$]')
tax.set_xlabel('Temperature [K]')
ax.set_xlim(1e-3, None)
tax.set_xlim(100, None)
ax.legend(lines, labels, loc='upper left', fontsize='small')
plt.savefig('msis21.png', dpi=300)
plt.show()
# %%
