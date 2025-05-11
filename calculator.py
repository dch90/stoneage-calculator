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

def get_distribution_dict(i_base, i_hp, i_at, i_df, i_sp):
    base = [i_hp, i_at, i_df, i_sp]  

    # New structure: derived stat -> set of modifiers
    derived_to_modifiers = defaultdict(lambda: defaultdict(int))

    # For each modifier, track which stats it's already linked to (optional, avoids extra work)
    for mod in B:
        for dist in A:
            s = combine_stats(base, dist, mod)
            derived = compute_derived(s, i_base)
            derived_to_modifiers[derived][mod] += 1
    return derived_to_modifiers

def get_all_case_count(stat_to_base):
    return sum(
        val for inner in stat_to_base.values()
        for val in inner.values()
    )

def get_specific_case_count(stat_to_base, key):
    return sum(
        stat_to_base[key].values()
    )

def calculate_chances(stat_to_base):
    all_possible_cases_count = get_all_case_count(stat_to_base)
    per_dict = defaultdict(lambda: defaultdict(float))
    for stat in stat_to_base.keys():
        stat_cases_count = get_specific_case_count(stat_to_base, stat)
        if (2,2,2,2) in stat_to_base[stat].keys():
            print_debug(stat)
            per_dict[stat] = {
                "base_chance": round(
                    (stat_to_base[stat][(2,2,2,2)] / sum(stat_to_base[stat].values()))*100,
                    5
                ),
                "encounter_chance": round((stat_cases_count / all_possible_cases_count) * 100, 5),
                "max": True
            }
        else:
            per_dict[stat] = {
                "base_chance": 0,
                "encounter_chance": round((stat_cases_count / all_possible_cases_count) * 100, 5),
                "max": False
            }
    return per_dict

def represent_s_pet(i_base, i_hp, i_at, i_df, i_sp):
    base = [x + 4.5 for x in [i_hp, i_at, i_df, i_sp]]
    stat = compute_derived(base, i_base)
    return f"{stat[1]} {stat[2]} {stat[3]} {stat[0]}"

def formatted_distribution(per_dict, max_only=True, sort_key="base_chance"):
    return_str = ""
    for stat, per_d in sorted(per_dict.items(), key=lambda x: x[1][sort_key], reverse=True):
        if max_only is False:
            return_str += f"{stat[1]} {stat[2]} {stat[3]} {stat[0]}:\n"
            return_str += f"    맥스 베이스일 확률: {per_d['base_chance']}%\n"
            return_str += f"    포획시 해당 스탯일 확률: {per_d['encounter_chance']}%\n"
        elif per_d["max"] is max_only:
            return_str += f"{stat[1]} {stat[2]} {stat[3]} {stat[0]}:\n"
            return_str += f"    맥스 베이스일 확률: {per_d['base_chance']}%\n"
            return_str += f"    포획시 해당 스탯일 확률: {per_d['encounter_chance']}%\n"

    return return_str

def pet_calculate(i_base, i_hp, i_at, i_df, i_sp, max_only=True, sort_key="base_chance"):
    distribution_dict = get_distribution_dict(i_base, i_hp, i_at, i_df, i_sp)
    chance_dict = calculate_chances(distribution_dict)
    return formatted_distribution(chance_dict, max_only, sort_key)
