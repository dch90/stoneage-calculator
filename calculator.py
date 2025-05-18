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

import math
from functools import reduce
from operator import mul
from itertools import product
from collections import defaultdict
from decimal import Decimal, getcontext

getcontext().prec = 50  # Set high enough precision

DEBUG=False

def print_debug(s):
    if DEBUG is True:
        print(s)

def round_to_significant(x, sig=3):
    if x == 0:
        return 0
    else:
        return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)

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

def compute_dist_prob(x_tuple):
    n = sum(x_tuple)
    k = len(x_tuple)
    numerator = math.factorial(n)
    denominator = reduce(mul, (math.factorial(x) for x in x_tuple))
    probability = (numerator / denominator) * (1 / k) ** n
    return probability

A = generate_distribution_combinations()
B = generate_signed_combinations()

def get_distribution_dict(i_base, i_hp, i_at, i_df, i_sp):
    base = [i_hp, i_at, i_df, i_sp]  

    # New structure: derived stat -> set of modifiers
    derived_to_modifiers = defaultdict(lambda: defaultdict(list[tuple]))

    # For each modifier, track which stats it's already linked to (optional, avoids extra work)
    for mod in B:
        for dist in A:
            s = combine_stats(base, dist, mod)
            derived = compute_derived(s, i_base)
            derived_to_modifiers[derived][mod].append(dist)
    return derived_to_modifiers

def compute_max_base_chance(stat_to_base, stat):
    if (2,2,2,2) not in stat_to_base[stat].keys():
        return 0
    all_base_count = sum([len(stat_to_base[stat][base]) for base in stat_to_base[stat].keys()])
    if all_base_count == 0:
        return 1
    max_base_count = len(stat_to_base[stat][(2,2,2,2)])
    return (max_base_count / all_base_count)

def compute_encounter_chance(stat_to_base, stat):
    prob = 0
    for base in stat_to_base[stat]:
        for dist in stat_to_base[stat][base]:
            prob += compute_dist_prob(dist)
    return (prob / 625)


def calculate_chances(stat_to_base):
    per_dict = defaultdict(lambda: defaultdict(float))
    for stat in stat_to_base.keys():
        max_base_chance = compute_max_base_chance(stat_to_base, stat)
        per_dict[stat] = {
            "base_chance": max_base_chance,
            "encounter_chance": compute_encounter_chance(stat_to_base, stat),
            "max": max_base_chance > 0
        }
    return per_dict

def represent_s_pet(i_base, i_hp, i_at, i_df, i_sp):
    base = [x + 4.5 for x in [i_hp, i_at, i_df, i_sp]]
    stat = compute_derived(base, i_base)
    return f"{stat[1]} {stat[2]} {stat[3]} {stat[0]}"

def format_korean_number(n: int) -> str:
    units = ['', '만', '억', '조', '경', '해']
    parts = []
    i = 0
    while n > 0 and i < len(units):
        n, remainder = divmod(n, 10_000)
        if remainder:
            parts.append(f"{remainder}{units[i]}")
        i += 1
    return ' '.join(reversed(parts)) if parts else '0'

def one_in_x_korean(p: float) -> str:
    if p <= 0:
        return "불가능"  # "Impossible" in Korean
    x = round(1 / p)
    return format_korean_number(x)


def formatted_distribution(per_dict, max_only=True, sort_key="base_chance"):
    return_str = ""
    for stat, per_d in sorted(per_dict.items(), key=lambda x: x[1][sort_key], reverse=True):
        if max_only is False:
            return_str += f"{stat[1]}{stat[2]}{stat[3]}{stat[0]}- {stat[1]} {stat[2]} {stat[3]} {stat[0]}:\n"
            return_str += f"    맥스 베이스일 확률: {round_to_significant(per_d['base_chance'] * 100)}%\n"
            return_str += f"    페트 등장/출현 확률: {round_to_significant(per_d['encounter_chance'] * 100)}%"
            return_str += f" ({one_in_x_korean(per_d['encounter_chance'])} 중 1)\n" if per_d['encounter_chance'] < 1 else "\n"
        elif per_d["max"] is max_only:
            return_str += f"{stat[1]}{stat[2]}{stat[3]}{stat[0]} - {stat[1]} {stat[2]} {stat[3]} {stat[0]}:\n"
            return_str += f"    맥스 베이스일 확률: {round_to_significant(per_d['base_chance'] * 100)}%\n"
            return_str += f"    페트 등장/출현 확률: {round_to_significant(per_d['encounter_chance'] * 100)}%"
            return_str += f" ({one_in_x_korean(per_d['encounter_chance'])} 중 1)\n" if per_d['encounter_chance'] < 1 else "\n"
    return return_str

def pet_calculate(distribution_dict, max_only=True, sort_key="base_chance"):
    # distribution_dict = get_distribution_dict(i_base, i_hp, i_at, i_df, i_sp)
    chance_dict = calculate_chances(distribution_dict)
    return formatted_distribution(chance_dict, max_only, sort_key)
