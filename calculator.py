'''
Program to find level 1 pet stats

Pet stats are: HP, Att, Def, Agi.

A pet is generated with a random base where each stat can added
integer values from the set { -2, -1, 0, 1, 2 }

A pet with max base has stats with { +2, +2, +2, +2 } base, and it
is the kind of pet that user want the most.

According to different base distructions, there are different possible
stats for a level 1 Pet.

This program aims to judge a level 1 pet and potentially find which
base stat it is assigned.

Features:

1. Get all possible level 1 stats with max base
2. Get all possible level 1 stats exclusive to max base
'''

from itertools import product
from collections import defaultdict

DEBUG=False

def print_debug(s):
    if DEBUG is True:
        print(s)

def generate_distribution_combinations(total=10, buckets=4):
    return [combo for combo in product(range(total + 1), repeat=buckets) if sum(combo) == total]

def generate_signed_combinations(slots=4, values=range(-2, 3)):
    return list(product(values, repeat=slots))

def combine_stats(base, dist, mod):
    return [b + d + m for b, d, m in zip(base, dist, mod)]

def compute_derived(s, i_base):
    # Apply i_base scaling to all values in s
    scaled = [x * i_base / 100 for x in s]

    hp = scaled[0] * 4 + scaled[1] + scaled[2] + scaled[3]
    attack = scaled[0] * 0.1 + scaled[1] + scaled[2] * 0.1 + scaled[3] * 0.05
    defense = scaled[0] * 0.1 + scaled[1] * 0.1 + scaled[2] + scaled[3] * 0.05
    speed = scaled[3]

    return (
        int(hp),
        int(attack),
        int(defense),
        int(speed)
    )

A = generate_distribution_combinations()
B = generate_signed_combinations()

def pet_calculate(i_base, i_hp, i_at, i_df, i_sp):
    base = [i_hp, i_at, i_df, i_sp]  

    # New structure: derived stat -> set of modifiers
    derived_to_modifiers = defaultdict(lambda: defaultdict(int))

    # For each modifier, track which stats it's already linked to (optional, avoids extra work)
    for mod in B:
        for dist in A:
            s = combine_stats(base, dist, mod)
            derived = compute_derived(s, i_base)
            derived_to_modifiers[derived][mod] += 1
    # return derived_to_modifiers
    per_dict = defaultdict(float)
    for stat in derived_to_modifiers.keys():
        if (2,2,2,2) in derived_to_modifiers[stat].keys():
            print_debug(stat)
            per_dict[stat] = round(
                (derived_to_modifiers[stat][(2,2,2,2)] / sum(derived_to_modifiers[stat].values()))*100,
                2
            )
    return per_dict

def represent_s_pet(i_base, i_hp, i_at, i_df, i_sp):
    base = [x + 4.5 for x in [i_hp, i_at, i_df, i_sp]]
    stat = compute_derived(base, i_base)
    return f"{stat[0]} {stat[1]} {stat[2]} {stat[3]}"

def formatted_distribution(distribution):
    return_str = ""
    for stat, per in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        return_str += f"{stat[0]} {stat[1]} {stat[2]} {stat[3]}: {per}%\n"
    return return_str