import json
from pathlib import Path
import re
import sys

import math
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from scipy.cluster.hierarchy import dendrogram
import networkx as nx
import pydot
import graphviz

from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import matthews_corrcoef as mcc

REPLACEMENT = "https://www.gerbrand.dev/"
IGNORE = set(
    [
        "Mana Crypt",
        "Sol Ring",
        "Chrome Mox",
        "Misty Rainforest",
        "Polluted Delta",
        "Scalding Tarn",
        "Windswept Heath",
        "Flooded Strand",
        "Marsh Flats",
        "Arid Mesa",
        "Verdant Catacombs",
        "Bloodstained Mire",
        "Wooded Foothills",
        "Swamp",
        "Plains",
        "Island",
        "Mountain",
        "Forest",
        "Snow-Covered Swamp",
        "Snow-Covered Plains",
        "Snow-Covered Island",
        "Snow-Covered Mountain",
        "Snow-Covered Forest",
        "Tundra",
        "Taiga",
        "Bayou",
        "Underground Sea",
        "Savannah",
        "Badlands",
        "Scrubland",
        "Tropical Island",
        "Volcanic Island",
        "Plateau",
        "Hallowed Fountain",
        "Watery Grave",
        "Blood Crypt",
        "Stomping Ground",
        "Temple Garden",
        "Godless Shrine",
        "Steam Vents",
        "Overgrown Tomb",
        "Sacred Foundry",
        "Breeding Pool",
        "Command Tower",
        "City of Brass",
        "Mana Confluence",
        "Gemstone Caverns",
        "Exotic Orchard",
        "Morphic Pool",
        "Fetid Heath",
        "Spire of Industry",
        "Cascade Bluffs",
        "Prismatic Vista",
        "Forbidden Orchard",
        "Tarnished Citadel",
        "Undergrowth Stadium",
        "Nurturing Peatland",
        "Adarkar Wastes",
        "Underground River",
        "Sulfurous Springs",
        "Karplusan Forest",
        "Brushland",
        "Caves of Koilos",
        "Shivan Reef",
        "Llanowar Wastes",
        "Battlefield Forge",
        "Yavimaya Coast",
        "Talisman of Conviction",
        "Talisman of Creativity",
        "Talisman of Curiosity ",
        "Talisman of Dominance ",
        "Talisman of Hierarchy ",
        "Talisman of Impulse",
        "Talisman of Indulgence",
        "Talisman of Progress",
        "Talisman of Resilience",
        "Talisman of Unity",
        "Arcane Signet",
        "Azorius Signet",
        "Boros Signet",
        "Dimir Signet",
        "Golgari Signet",
        "Gruul Signet",
        "Izzet Signet",
        "Orzhov Signet",
        "Rakdos Signet",
        "Selesnya Signet",
        "Simic Signet",
        "Sunbaked Canyon",
        "Waterlogged Grove",
        "Silent Clearing",
        "Nurturing Peatland",
        "Fiery Islet",
    ]
)

CARDFILE = "cards.json"
if Path(CARDFILE).exists():
    with open(CARDFILE, "r") as f:
        scryfall = json.load(f)
        print(len(scryfall), "loaded cards")
else:
    print(
        CARDFILE,
        "does not exist. Generate using https://github.com/konradHoeffner/mtgslides and copy here.",
    )
    sys.exit()

DECKFILE = "decks.json"
if Path(DECKFILE).exists():
    with open(DECKFILE, "r") as f:
        decks = json.load(f)
        print(len(decks), "loaded decks")
else:
    print(DECKFILE, "does not exist. Run main.py first.")
    sys.exit()

featurearray = []
allcards = set()

for key in decks.keys():
    d = dict()
    cards = decks[key]
    cards = set(cards)
    cards.difference_update(IGNORE)
    allcards.update(cards)
    cards = list(cards)
    cards.sort()
    d["cards"] = cards
    featurearray.append(d)

print(len(allcards), "Used cards")
# print(allcards)
carddict = dict()
for card in allcards:
    carddict[card] = []

for key in decks.keys():
    d = dict()
    cards = decks[key]
    cards = set(cards)
    cards.difference_update(IGNORE)
    for card in cards:
        carddict[card].append(key)

cardarray = []
newcarddict = dict()
for key in carddict.keys():
    d = dict()
    localdecks = carddict[key]
    if len(localdecks) > 9:
        localdecks.sort()
        d["decks"] = localdecks
        cardarray.append(d)
        newcarddict[key] = localdecks

carddict = newcarddict


def label(i):
    if i < len(carddict):
        return list(carddict.keys())[i]
    return i


vectorizer = DictVectorizer()
data = vectorizer.fit_transform(cardarray).toarray()
# print(data)
inverse = vectorizer.inverse_transform(data)
# print(inverse[0])
# print(label(0),label(2))
# print(mcc(data[0],data[2])


# https://github.com/scikit-learn/scikit-learn/blob/70cf4a676caa2d2dad2e3f6e4478d64bcb0506f7/examples/cluster/plot_hierarchical_clustering_dendrogram.py
def plot_dendrogram(model, **kwargs):
    # The number of observations contained in each cluster level
    no_of_observations = np.arange(2, model.children_.shape[0] + 2)
    # Create linkage matrix and then plot the dendrogram
    linkage_matrix = np.column_stack([model.children_, model.distances_, no_of_observations]).astype(float)
    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)
    return linkage_matrix


colormap = {
    frozenset({"R"}): "red",
    frozenset({"B"}): "gray",
    frozenset({"U"}): "lightblue",
    frozenset({"W"}): "white",
    frozenset({"G"}): "lightgreen",
    frozenset(): "sandybrown",
}


def color(i):
    l = label(i)
    if not l in scryfall:
        #    if not isinstance(l,int):
        #        print(l)
        return "white"
    card = scryfall[l]
    colors = frozenset(card["colors"])
    if colors in colormap:
        return colormap[colors]
    # print(colors)
    # if card["type_line"].startswith("Artifact"):
    #    return "brown"
    return "yellow"


# https://stackoverflow.com/questions/9838861/scipy-linkage-format
# https://datascience.stackexchange.com/questions/101854/how-to-visualize-a-hierarchical-clustering-as-a-tree-of-labelled-nodes-in-python
def showTree(linkage_matrix):
    G = nx.Graph()
    n = len(linkage_matrix)
    for i in range(n):
        row = linkage_matrix[i]
        G.add_node(label(int(row[0])), fillcolor=color(int(row[0])), style="filled")
        G.add_node(label(int(row[1])), fillcolor=color(int(row[1])), style="filled")
        G.add_edge(label(int(row[0])), label(n + i + 1), len=1 + 0.1 * (math.log(1 + row[2])))
        G.add_edge(label(int(row[1])), label(n + i + 1), len=1 + 0.1 * (math.log(1 + row[2])))
    # for key,value in astcolors.items():
    # G.add_node(key,fillcolor=value,style="filled")
    dot = nx.nx_pydot.to_pydot(G).to_string()
    dot = graphviz.Source(dot, engine="neato")
    dot.render(format="pdf", filename="tree")
    dot.render(format="svg", filename="tree")


def l1(x, y):
    # x and y are both cards expressed as vectors of decks
    # but we don't know which card x and y stand for
    # print(x)
    sum = 0
    for i in range(len(x)):
        # here we should only count decks x[i] and y[i] if they contain both
        sum += abs(x[i] - y[i])

    # we now have the number of decks, which have one of the cards and not the other
    # we may get a better result by scaling this number by the number of decks that have the color identity to include both
    return sum
    # int(edist.eval(data[int(x[0])], data[int(y[0])]))


m = pairwise_distances(data, metric=l1)
print(m)

# todo: transform into real code
# def distance(card1,card2):
# max = number of decks that could contain card 1 and 2 based on color identity
# count = number of decks that contain one card but not the other
# return count / max
# thought out example 1: brainstorm and ponder
# number of decks: 100
# number of decks with blue: 80
# number of decks exactly one of brainstorm and ponder: 5
# distance would then be 5/80
# thought out example 2: abrupt decay and vindicate
# number of decks with WUB: 30
# number of decks with exactly one of them: 10
# 10/30, no that is too large, this calculation is wrong
# we should instead only count decks with the color identity of both
def createOurOwnDistanceMatrix():
    n = len(cards)
    O = np.zeros((n, n))
    for i in range(len(decks)):
        for j in range(i):
            dist = l1(decks[list(decks.keys())[i]], decks[list(decks.keys())[j]])
            O[i][j] = dist
            O[j][i] = dist
    return O


O = createOurOwnDistanceMatrix()


def calculateDeckIdentities():
    deckIdentities = []
    keys = list(decks.keys())
    for i in range(len(keys)):
        deck = keys[i]
        cs = decks[deck]
        colors = set()
        # we don't know who the commander is, so build the union of the color identities of all cards in the deck instead
        for card in cs:
            if card in scryfall:
                colors.update(set(scryfall[card]["color_identity"]))
        # print("Colors for",deck,colors)
        deckIdentities.append(colors)
    return deckIdentities


# print(type(decks))

# deckIdentities = calculateDeckIdentities()


def clusterTree(data):
    N_CLUSTERS = 10
    # precomputed requires a distance matrix
    clustering = AgglomerativeClustering(
        linkage="average",
        n_clusters=N_CLUSTERS,
        compute_distances=True,
        affinity="precomputed",
    )
    clustering.fit(O)
    # clustering = AgglomerativeClustering(linkage="average", n_clusters=N_CLUSTERS, compute_distances=True, affinity="l1")
    # clustering.fit(data)
    # plot_dendrogram(clustering, labels=clustering.labels_)
    linkage_matrix = plot_dendrogram(clustering, show_leaf_counts=False)
    # print(linkage_matrix)
    showTree(linkage_matrix)
    # plt.show()


clusterTree(data)
