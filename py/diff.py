# compare dist/cards.json to dist/cards.json.old and give a markdown table report
# requires checking out an old version of dist/cards.json to dist/cards.old.json
import json
from itertools import combinations, chain
import pytablewriter as ptw
import sys

CARDFILE = "./dist/data/cards.json"
CARDFILE_OLD = "./dist/data/cards.old.json"
DIFFFILE = "./dist/data/cards.diff.json"
MIN_COUNT = 3
MIN_DIFF = 5
MIN_SUPER_DIFF = 1
MAX_DIFF = 1000  # workaround to exclude outliers caused by errors in the data

with open(CARDFILE, "r") as f:
    cards = json.load(f)
with open(CARDFILE_OLD, "r") as f:
    cardsOld = json.load(f)

# optional parameter: minimum first release date, for example 2021-01-01 to get only cards from 2021 onwards
if len(sys.argv)>1:
    MIN_DATE = sys.argv[1]
    INDEX_URL = "https://konradhoeffner.github.io/mtgindex/mtgindex.json"
    from urllib.request import urlopen
    index = json.loads(urlopen(INDEX_URL).read().decode("utf-8"))
    cards = dict(filter(lambda item: index[item[0]]["date"] >= MIN_DATE, cards.items()))
    cardsOld = dict(filter(lambda item: index[item[0]]["date"] >= MIN_DATE, cardsOld.items()))

keys = list(cards.keys())
keys.sort()

nan = float("NaN")
diff = dict()
diff_matrix = list()
for key in keys:
    if key in cardsOld:
        old = cardsOld[key]
    else:
        old = {"count":0, "superrank":nan, "rank":nan, "identity_rank":nan, "supercent": 0}
    new = cards[key]
    if new["count"] < MIN_COUNT:
        continue  # skip cards that are only in very few decks
    # lower numbers are higher ranks, so upranking reduces the rank
    count = new["count"]
    countdiff = count - old["count"]
    rank = new["rank"]
    superrank = new["superrank"]
    rankdiff = old["rank"] - rank
    superrankdiff = old["superrank"] - superrank
    irank = new["identity_rank"]
    irankdiff = old["identity_rank"] - irank
    supercent = new["supercent"]
    supercentdiff = supercent - old["supercent"]
    # if abs(rank) < MIN_DIFF and abs(superrank) < MIN_SUPER_DIFF:
    #    continue
    # if max(abs(rankdiff), abs(superrankdiff)) > MAX_DIFF:
    #    continue
    new["countdiff"] = countdiff
    new["rankdiff"] = rankdiff
    new["superrankdiff"] = superrankdiff
    matrix_entry = [
        key,
        count,
        countdiff,
        rank,
        rankdiff,
        superrank,
        superrankdiff,
        supercent,
        supercentdiff,
        new["color_identity"],
        irank,
        irankdiff,
    ]
    diff[key] = new
    diff_matrix.append(matrix_entry)

with open(DIFFFILE, "w") as f:
    json.dump(diff, f, indent=2)
    print("saved", len(keys), "diffs to", DIFFFILE)


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


COLORS = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}
COLOR_IDENTITIES = powerset(COLORS.keys())


def markdown():
    headers = ["Card", "Count", "ΔCount", "Rank", "ΔRank", "SRank", "ΔSRank","% rel","Δ% rel"]

    byrankdiff = sorted(diff_matrix, key=lambda row: row[2], reverse=True)[0:10]
    writer = ptw.MarkdownTableWriter(table_name="Top Increased Count", headers=headers, value_matrix=byrankdiff)
    writer.write_table()
    print()
    byrankdiff = sorted(diff_matrix, key=lambda row: row[2])[0:10]
    writer = ptw.MarkdownTableWriter(table_name="Top Decreased Count", headers=headers, value_matrix=byrankdiff)
    writer.write_table()

    headers = ["Card", "Count", "ΔCount", "% rel","Δ% rel"]
    for identity in COLOR_IDENTITIES:
        identity = set(identity)
        byidentity = map(lambda row: row[0:3] + row[7:9] + row[10:12], filter(lambda card: identity == set(card[9]), diff_matrix))
        byidentity = sorted(byidentity, key=lambda row: row[1], reverse=True)[0:85]
        if len(byidentity) < 1:
            continue
        identityName = "".join(identity)
        if identityName in COLORS:
            identityName = COLORS[identityName]
        if identityName == "":
            identityName = "Colorless"
        print()
        writer = ptw.MarkdownTableWriter(table_name="Top " + identityName, headers=headers, value_matrix=byidentity)
        writer.write_table()


markdown()
