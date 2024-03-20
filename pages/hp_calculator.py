
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

def quick_calc(hds, bonuses, first_level_hd = None):
    mean_hp = 0
    max_hp = 0

    for n, nb_dice in hds.items():
        mean_rolls = [((n+1)/2) for _ in range(nb_dice)]
        max_rolls = [n for _ in range(nb_dice)]
        if first_level_hd is not None and len(mean_rolls) > 0 and n == first_level_hd:
            mean_rolls[0] = n
        mean_hp += np.sum(mean_rolls)
        max_hp += np.sum(max_rolls)

    ttl_from_con = sum(hds.values()) * bonuses['con']
    ttl_from_other = sum(hds.values()) * bonuses['other']
    mean_hp += ttl_from_con + ttl_from_other
    max_hp += ttl_from_con + ttl_from_other

    return mean_hp, max_hp

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

    ttl_from_con = sum(hds.values()) * bonuses['con']
    ttl_from_other = sum(hds.values()) * bonuses['other']
    
    for i in range(n_samples):
        from_rolls = roll_hp(hds, first_level_hd)
        ttl_from_rolls.append(from_rolls)
        ttl_with_bonus.append(from_rolls + ttl_from_con + ttl_from_other)

    fig, ax = plt.subplots()
    ax.hist(ttl_with_bonus)
    ax = rework_y_axis(ax, n_samples)
    plt.xlabel('Total HP')
    plt.xlabel('Probability of Total HP')
    st.pyplot(fig)
    return ttl_with_bonus

    
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
mean_hp, max_hp = quick_calc(hds, bonuses, first_level_hd)
mean_hp = round(mean_hp, 3)
max_hp = int(max_hp)
st.write(f'expected HP: {mean_hp}, max HP: {max_hp}')


st.write('Query: what is the probability of the below total HP.')
hp_query = st.number_input('How often will total be less/greater than:', value = int(mean_hp), min_value = 0, max_value = 2 * max_hp)
    
if st.button('Roll!'):
    ttl_with_bonus = bootstrap_hp(hds, bonuses, first_level_hd)
    
    sorted_ttls = sorted(ttl_with_bonus)
    ttl_median = round(np.median(ttl_with_bonus), 3)
    ttl_mean = round(np.median(ttl_with_bonus), 3)
    perc_10 = sorted_ttls[int(len(ttl_with_bonus) * .1)]
    perc_90 = sorted_ttls[int(len(ttl_with_bonus) * .9)]
    st.write(f'mean: {ttl_mean}, median: {ttl_median}')
    st.write(f'10th percentile: {perc_10}, 90th: {perc_90}')
    
    nb_less = len([x for x in sorted_ttls if x < hp_query])
    nb_more = len([x for x in sorted_ttls if x >= hp_query])
    st.write(f'{round(100 * nb_less / len(ttl_with_bonus), 3)}% samples with fewer than {hp_query} HP, {round(100 * nb_more / len(ttl_with_bonus), 3)}% samples with greater or equal to {hp_query} HP')

st.button("Reset", type="primary")

