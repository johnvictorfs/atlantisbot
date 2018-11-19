import json

with open('player_activities.json') as f:
    old = json.load(f)

with open('player_activities2.json') as f:
    new = json.load(f)

new_keys = set(new) - set(old)
difference = {}
for key, item in new.items():
    if key not in new_keys:
        diff_items = [act for act in item if act not in old.get(key)]
        difference[key] = diff_items
difference.update({k: new[k] for k in new_keys})

print(difference)
