import json
from collections import Counter
from pathlib import Path
import sys
from urllib.request import urlopen

# import re

INDEX_URL = "https://konradhoeffner.github.io/mtgindex/mtgindex.json"
DECKFILE = "./dist/decks.json"
STATFILE = "./dist/cards.json"

index = json.loads(urlopen(INDEX_URL).read().decode("utf-8"))
indexkeys = index.keys()
print(len(indexkeys), "index cards loaded")

if not Path(DECKFILE).exists():
    print(DECKFILE, "does not exist, aborting.")
    sys.exit(1)

with open(DECKFILE, "r") as f:
    decks = json.load(f)
print(len(decks), "decks loaded")

cardCounter = Counter()

for deckName in decks:
    cardCounter.update(decks[deckName])

print("Most common:", cardCounter.most_common(5))

cardStats = dict()
for cardName in cardCounter:
    if not cardName in index:
        # index has problems with split cards, try first half
        cardName = cardName.split("//")[0].strip()
        if not cardName in index:
            print(cardName, "not in index")
            continue
    cardStats[cardName] = index[cardName]
    cardStats[cardName]["count"] = cardCounter[cardName]

with open(STATFILE, "w") as f:
    json.dump(cardStats, f, indent=2)
    print("saved", len(cardCounter), "cards to", STATFILE)
