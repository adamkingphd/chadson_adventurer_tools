
import pandas as pd
import numpy as np
import scipy as sp

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


def dN(n, n_rolls = 1):
    return np.random.randint(1, n + 1, size = n_rolls)

def d6(n_rolls = 1):
    return dN(6, n_rolls)

def d8(n_rolls = 1):
    return dN(8, n_rolls)

def d10(n_rolls = 1):
    return dN(10, n_rolls)

def d12(n_rolls = 1):
    return dN(12, n_rolls)

def roll_hp(hds : dict, first_level_hd = None):
    ttl_from_rolls = 0
    for n, nb_dice in hds.items():
        rolls = dN(n, nb_dice)
        # first level is automatically max
        if first_level_hd is not None and len(rolls) > 0 and n == first_level_hd:
            rolls[0] = first_level_hd
        ttl_from_rolls += np.sum(rolls)
    
    return ttl_from_rolls 


def rework_y_axis(ax, n_samples):
    ticks = []
    new_tick_labels = []

    for tick in ax.get_yticks():
        ticks.append(tick)
        new_label = round(tick / n_samples, 3)
        new_tick_labels.append(new_label)

    ax.set_yticks(ticks, labels = new_tick_labels)
    return ax

def bootstrap_hp(hds, bonuses, first_level_hd, n_samples = 10_000):
    ttl_from_rolls, ttl_with_bonus = [], []

    ttl_from_con = sum(hds.values()) + bonuses['con']
    ttl_from_other = sum(hds.values()) + bonuses['other']

    for i in range(n_samples):
        from_rolls = roll_hp(hds, first_level_hd)
        ttl_from_rolls.append(from_rolls)
        ttl_with_bonus.append(from_rolls + ttl_from_con + ttl_from_con)

    fig, ax = plt.subplots()
    ax.hist(ttl_with_bonus)
    ax = rework_y_axis(ax, n_samples)
    st.pyplot(fig)    

    st.write(f'mean: {np.mean(ttl_with_bonus)}, median: {np.median(ttl_with_bonus)}')
    perc_10 = sorted(ttl_with_bonus)[int(n_samples * .1)]
    perc_90 = sorted(ttl_with_bonus)[int(n_samples * .9)]
    st.write(f'10th percentile: {perc_10}, 90th: {perc_90}')

st.title('HP Calculator')
hd_cols = st.columns(4)

hds = {}
for i, (col, n) in enumerate(zip(hd_cols, [6, 8, 10, 12])):
    with col:
        st.header(f"d{n}")
        hds[n] = st.number_input(f'number of d{n} HD', value = 0, min_value = 0, max_value = 20, key = n)

st.write(f'Total level: {sum(hds.values())}')

first_level_hd = st.radio('HD for first level',
    ['d6', 'd8', 'd10', 'd12'])
first_level_hd = int(first_level_hd.replace('d', ''))

if first_level_hd not in hds or hds[first_level_hd] == 0:
    sorted_hd = sorted(hds, key = hds.get, reverse = True)
    print(sorted_hd)
    st.write(f'Warning! HD for first level not represented in counts above. Assuming first level is d{sorted_hd[0]} instead.')
    first_level_hd = sorted_hd[0]

bonuses = {}
bonus_cols = st.columns(2)
with bonus_cols[0] as col:
    st.header('CON bonus')
    bonuses['con'] = st.number_input(f'CON bonus', value = 0, min_value = -2, max_value = 8, key = 'con')

with bonus_cols[1] as col:
    st.header('other bonus')
    bonuses['other'] = st.number_input(f'any other bonus (e.g., feats)', value = 0, min_value = -5, max_value = 5, key = 'other')

st.write(f'Total bonus per level: {sum(bonuses.values())}')


st.button("Reset", type="primary")
if st.button('Roll!'):
    bootstrap_hp(hds, bonuses, first_level_hd)

