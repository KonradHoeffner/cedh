import json
from collections import Counter
from pathlib import Path
import sys
from urllib.request import urlopen
from itertools import combinations, chain

# load stuff ################################################################

INDEX_URL = "https://konradhoeffner.github.io/mtgindex/mtgindex.json"
DECKFILE = "./dist/decks.json"
STATFILE = "./dist/cards.json"
STATFILE_JS = "./dist/cards.js"

index = json.loads(urlopen(INDEX_URL).read().decode("utf-8"))
indexkeys = index.keys()
print(len(indexkeys), "index cards loaded")

if not Path(DECKFILE).exists():
    print(DECKFILE, "does not exist, aborting.")
    sys.exit(1)

with open(DECKFILE, "r") as f:
    decks = json.load(f)
print(len(decks), "decks loaded")

# cards with counts #########################################################
# I <3 Python, it's so compact.
cardCounter = Counter()
for deckName in decks:
    cardCounter.update(decks[deckName]["mainboard"])
print("Most common:", cardCounter.most_common(5))

identityCounter = Counter()

cardStats = dict()
for cardName in cardCounter:
    if not cardName in index:
        # index has problems with split cards, try first half
        cardName = cardName.split("//")[0].strip()
        if not cardName in index:
            print(cardName, "not in index")
            continue
    entry = index[cardName]
    entry["name"] = cardName
    entry["count"] = cardCounter[cardName]
    entry["percent"] = int(100 * cardCounter[cardName] / len(decks))
    entry["types"] = entry["type_line"].split("\u2014")[0].strip().split(" ")
    cardStats[cardName] = entry

    identityCounter[frozenset(entry["color_identity"])] += 1

# superidentity #############################################################
for deckName in decks:
    deck = decks[deckName]
    commanders = deck["commanders"]
    # workaround for index problems
    if commanders[0] == "Kenrith, the Returned King":
        deck["color_identity"] = frozenset(["W", "U", "R", "B", "R", "G"])
        continue
    deckIdentity = set().union(
        *list(map(lambda commander: frozenset(index[commander.split("//")[0].strip()]["color_identity"]), commanders))
    )
    deck["color_identity"] = deckIdentity

superIdentityCounter = Counter()
for identity in identityCounter:
    # superidentities = set(filter(lambda id: id.issuperset(identity), identityCounter.keys()))
    # superdecks = filter(lambda deck: frozenset(deck["color_identity"]) in superidentities,decks.values())
    superdecks = filter(lambda deck: frozenset(deck["color_identity"]).issuperset(identity), decks.values())
    superIdentityCounter[identity] = len(list(superdecks))

# supercent as abbreviation for "super identity percentage" so table columns fit small screens
for cardName in cardStats:
    # print(cardName,frozenset(cardStats[cardName]["color_identity"]))
    cardStats[cardName]["supercent"] = int(
        100 * cardCounter[cardName] / superIdentityCounter[frozenset(cardStats[cardName]["color_identity"])]
    )

# ranking ###################################################################


def rank(cardNames, on, key):
    cardNames.sort(key=lambda cardName: cardStats[cardName][on], reverse=True)
    for i in range(len(cardNames)):
        cardStats[cardNames[i]][key] = i + 1


# all cards
rank(list(cardStats.keys()), "count", "rank")
rank(list(cardStats.keys()), "supercent", "superrank")
# separately for each color identity
for identity in identityCounter:
    identityCards = list(filter(lambda cardName: frozenset(cardStats[cardName]["color_identity"]) == identity, cardStats.keys()))
    rank(identityCards, "count", "identity_rank")

#############################################################################

# color identity
# COLORS = frozenset({"W","U","B","R","G"})
# COLOR_IDENTITIES = frozenset(powerset(COLORS))
# print(COLOR_IDENTITIES)
# print(len(identityCounter),"color identities")
# print(identityCounter)

cardStats = dict(sorted(cardStats.items()))  # sort to minimize diff

with open(STATFILE, "w") as f:
    json.dump(cardStats, f, indent=2)
    print("saved", len(cardCounter), "cards to", STATFILE)

json_string = json.dumps(cardStats, indent=2)
with open(STATFILE_JS, "w") as f_js:
    f_js.write("const cards =\n" + json_string + ";")
    print("Saved", STATFILE_JS)
