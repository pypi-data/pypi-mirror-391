# %%
from __future__ import annotations
from datetime import datetime, UTC
import matplotlib
from iri20py import Iri2020, alt_grid
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
iri20 = Iri2020()
date = time = datetime(2022, 3, 22, 18, 0).astimezone(UTC)
glat = 42.6
glon = -71.2
_, ds20 = iri20.evaluate(
    date, glat, glon, np.arange(60, 801, 5)
)
# %%
ig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=300)
tax = ax.twiny()
species = ['O+', 'O2+', 'N+', 'NO+']
descs = ['O^+', 'O_2^+', 'N^+', 'NO^+']
# species = ['N+']
colors = ['r', 'g', 'b', 'm']
labels = []
lines = []
for spec, color, desc in zip(species, colors, descs):
    l21, = ds20[spec].plot(y='alt_km', ax=ax, color=color, lw=0.75)
    lines.extend([l21])
    labels.extend([f'${desc}$'])
ax.set_title('IRI-2020')
l21, = ds20['Te'].plot(y='alt_km', ax=tax, color='k', lw=0.75)
lines.extend([l21])
labels.extend(['$T_e$'])
l21, = ds20['Ti'].plot(y='alt_km', ax=tax, color='c', alpha=0.7, lw=0.75)
lines.extend([l21])
labels.extend(['$T_i$'])
ax.set_xscale('log')
ax.set_xlabel('Number Density [cm$^{-3}$]')
tax.set_xlabel('Temperature [K]')
ax.set_xlim(1e-3, None)
tax.set_xlim(100, None)
ax.legend(lines, labels, loc='upper left', fontsize='small')
plt.savefig('iri20.png', dpi=300)
plt.show()
# %%
