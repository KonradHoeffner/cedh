# compare dist/cards.json to dist/cards.json.old and give a markdown table report
import json
import pytablewriter as ptw

CARDFILE = "./dist/cards.json"
CARDFILE_OLD = "./dist/cards.old.json"
DIFFFILE = "./dist/cards.diff.json"
MIN_DIFF = 5
MIN_SUPER_DIFF = 1

with open(CARDFILE, "r") as f:
    cards = json.load(f)
with open(CARDFILE_OLD, "r") as f:
    cardsOld = json.load(f)

keys = list(set(cards.keys()).intersection(cardsOld.keys()))
keys.sort()

diff = dict()
for key in keys:
    old = cardsOld[key]
    new = cards[key]
    # lower numbers are higher ranks, so upranking reduces the rank
    rank = old["rank"]-new["rank"]
    superrank = old["superrank"]-new["superrank"]
    if abs(rank)<MIN_DIFF and abs(superrank)<MIN_SUPER_DIFF:
        continue
    entry = {"rank": rank, "superrank": superrank}
    diff[key] = entry

with open(DIFFFILE, "w") as f:
    json.dump(diff, f, indent=2)
    print("saved", len(keys), "diffs to", DIFFFILE)


def markdown():
    value_matrix = [[1,2,3,4,5]]
    writer = ptw.MarkdownTableWriter(
        table_name="Top Upranked",
        headers=["Card", "Rank", "ΔRank", "SRank", "ΔSRank"],
        value_matrix=value_matrix
        )
    writer.write_table()

markdown()
