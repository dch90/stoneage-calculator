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

def generate_bucket_combinations(total=10, buckets=4):
    results = []
    for combo in product(range(total + 1), repeat=buckets):
        if sum(combo) == total:
            results.append(combo)
    return results

def generate_signed_combinations(slots=4, values=(-2, -1, 0, 1, 2)):
    return list(product(values, repeat=slots))

def remove_duplicates_and_sort(data):
    # Remove duplicates by converting each inner list to a tuple, and then back to list
    unique_data = list({tuple(item) for item in data})
    # Sort based on the full list (indices 0 to 3)
    unique_data.sort()
    return unique_data


# Example usage
all_combinations = generate_signed_combinations()

base    = int( input("Enter Base: ") )+2
hp      = int( input("Enter HP: ") )+2
attack  = int( input("Enter Attack: ") )+2
defense = int( input("Enter Defense: ") )+2
agility = int( input("Enter Agility: ") )+2

level_one_stats = []

for comb in all_combinations:
    attGrowth = (attack + comb[0]) * base / 100
    defGrowth = (defense + comb[1]) * base / 100
    agiGrowth = (agility + comb[2]) * base / 100
    hpGrowth = (hp + comb[3]) * base / 100

    levelOneHp = int(hpGrowth * 4 + attGrowth + defGrowth + agiGrowth)
    levelOneAtt = int(hpGrowth / 10 + attGrowth + defGrowth / 10 + agiGrowth / 10)
    levelOneDef = int(hpGrowth / 10 + attGrowth /10 + defGrowth + agiGrowth / 10)
    levelOneAgi  = int(agiGrowth)

    level_one_stats.append(
        [ levelOneHp, levelOneAtt, levelOneDef, levelOneAgi ]
    )

sorted = remove_duplicates_and_sort(level_one_stats)

print("Level 1 stats:")
for i in sorted:
    print(i[0], i[1], i[2], i[3])
