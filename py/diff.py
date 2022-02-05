# compare dist/cards.json to dist/cards.json.old and give a markdown table report
# requires checking out an old version of dist/cards.json to dist/cards.old.json
import json
import pytablewriter as ptw

CARDFILE = "./dist/cards.json"
CARDFILE_OLD = "./dist/cards.old.json"
DIFFFILE = "./dist/cards.diff.json"
MIN_COUNT = 3
MIN_DIFF = 5
MIN_SUPER_DIFF = 1
MAX_DIFF = 100  # workaround to exclude outliers caused by errors in the data

with open(CARDFILE, "r") as f:
    cards = json.load(f)
with open(CARDFILE_OLD, "r") as f:
    cardsOld = json.load(f)

keys = list(set(cards.keys()).intersection(cardsOld.keys()))
keys.sort()

diff = dict()
diff_matrix = list()

for key in keys:
    old = cardsOld[key]
    new = cards[key]
    if min(new["count"], old["count"]) < MIN_COUNT:
        continue  # skip cards that are only in very few decks
    # lower numbers are higher ranks, so upranking reduces the rank
    count = new["count"]
    countdiff = count - old["count"]
    rank = new["rank"]
    superrank = new["superrank"]
    rankdiff = old["rank"] - rank
    superrankdiff = old["superrank"] - superrank
    if abs(rank) < MIN_DIFF and abs(superrank) < MIN_SUPER_DIFF:
        continue
    if max(abs(rankdiff), abs(superrankdiff)) > MAX_DIFF:
        continue
    entry = {
        "count": count,
        "countdiff": countdiff,
        "rank": rank,
        "rankdiff": rankdiff,
        "superrank": superrank,
        "superrankdiff": superrankdiff,
    }
    matrix_entry = [key, count, countdiff, rank, rankdiff, superrank, superrankdiff]
    diff[key] = entry
    diff_matrix.append(matrix_entry)

with open(DIFFFILE, "w") as f:
    json.dump(diff, f, indent=2)
    print("saved", len(keys), "diffs to", DIFFFILE)


def markdown():
    headers = ["Card", "Count", "ΔCount", "Rank", "ΔRank", "SRank", "ΔSRank"]
    
    byrankdiff = sorted(diff_matrix, key=lambda row: row[2], reverse=True)[0:5]
    writer = ptw.MarkdownTableWriter(table_name="Top Upcounted", headers=headers, value_matrix=byrankdiff)
    writer.write_table()

markdown()
