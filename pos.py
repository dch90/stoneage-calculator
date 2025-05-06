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

i_base = int(input("페트 초기계수 입력: "))
i_hp = int(input("페트 베이스 피 입력: "))
i_at = int(input("페트 베이스 공 입력: "))
i_df = int(input("페트 베이스 방 입력: "))
i_sp = int(input("페트 베이스 순 입력: "))
base = [i_hp, i_at, i_df, i_sp]

def generate_distribution_combinations(total=10, buckets=4):
    return [combo for combo in product(range(total + 1), repeat=buckets) if sum(combo) == total]

def generate_signed_combinations(slots=4, values=range(-2, 3)):
    return list(product(values, repeat=slots))

def combine_stats(base, dist, mod):
    return [b + d + m for b, d, m in zip(base, dist, mod)]

def compute_derived(s):
    # Apply i_base scaling to all values in s
    scaled = [x * i_base / 100 for x in s]

    hp = scaled[0] * 4 + scaled[1] + scaled[2] + scaled[3]
    attack = scaled[0] / 10 + scaled[1] + scaled[2] / 10 + scaled[3] / 10
    defense = scaled[0] / 10 + scaled[1] / 10 + scaled[2] + scaled[3] / 10
    speed = scaled[3]

    return (
        int(hp),
        int(attack),
        int(defense),
        int(speed)
    )

A = generate_distribution_combinations()
B = generate_signed_combinations()

# New structure: derived stat -> set of modifiers
derived_to_modifiers = defaultdict(set)

# For each modifier, track which stats it's already linked to (optional, avoids extra work)
for mod in B:
    seen_stats = set()
    for dist in A:
        s = combine_stats(base, dist, mod)
        derived = compute_derived(s)
        if derived not in seen_stats:
            derived_to_modifiers[derived].add(mod)
            seen_stats.add(derived)

per_dict = defaultdict(int)
for stat, b_mods in derived_to_modifiers.items():
    if (2,2,2,2) in b_mods:
        per_dict[stat] = round((1 / len(b_mods)) * 100, 2)

print(per_dict)

# target_modifier = (2, 2, 2, 2)
#
# # Filter stats where the *only* modifier is the one we're asking about
# unique_stats = [
#     stat for stat, mods in derived_to_modifiers.items()
#     if mods == {target_modifier}
# ]

# print(f"{len(unique_stats)} unique stats are exclusively produced by {target_modifier}:")
# for stat in unique_stats:
#     print(" ", stat)
