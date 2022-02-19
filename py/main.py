from crawler import Crawler
from urllib.request import urlopen, HTTPError
import json
from pathlib import Path
import re

import math
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from scipy.cluster.hierarchy import dendrogram
import networkx as nx
import pydot
import graphviz

LINKFILE = "links.json"
if Path(LINKFILE).exists():
    with open(LINKFILE, "r") as f:
        links = json.load(f)
        print(len(links), "loaded links")
else:
    crawler = Crawler("https://cedh-decklist-database.com/")
    crawler.run()
    print(len(crawler.links), "crawled links")
    links = crawler.links
    with open(LINKFILE, "w") as f:
        json.dump(links, f, indent=2)

PREFIX = "https://www.moxfield.com/"
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


def crawlDecks(links):
    decks = dict()
    for link in links:
        if not PREFIX in link:
            continue
        cards = set()
        url = link.replace(PREFIX, REPLACEMENT)
        try:
            text = urlopen(url).read().decode("utf-8")
        except HTTPError:
            print("Could not open", url)
            continue
        # print(text)
        title = re.search("Deck name: ([^\r\n]+)", text).group(1)
        title = re.sub("[^A-Za-z] ", "", title)

        commander = re.search("Commander\(s\):\r\n([^\r\n]+\r\n[^\r\n]*)", text, re.M).group(1)
        commander = commander.replace("\r\n", " ").strip()
        cards.add(commander)
        # print(commander,url)
        print(title, url)
        LEFT = "Mainboard (100):\r\n"
        if not LEFT in text:
            continue
        text = text[text.index(LEFT) + len(LEFT) :]
        RIGHT = "Considering"
        if RIGHT in text:
            text = text[: text.index(RIGHT)]
        # print(text)
        lines = text.split("\r\n")
        for line in lines:
            if not line.startswith("1 "):
                continue
            card = line.split("1 ")[1]
            cards.add(card)
        # cards.difference_update(IGNORE)
        while title in decks:
            title += "*"
        cardlist = list(cards)
        cardlist.sort()
        decks[title] = cardlist
        # print(cards)
    return decks


DECKFILE = "dist/data/decks.json"
if Path(DECKFILE).exists():
    with open(DECKFILE, "r") as f:
        decks = json.load(f)
        print(len(decks), "loaded decks")
else:
    decks = crawlDecks(links)
    print(len(decks), "crawled decks")
    with open(DECKFILE, "w") as f:
        json.dump(decks, f, indent=2)

featurearray = []
for key in decks.keys():
    d = dict()
    cards = decks[key]["mainboard"]
    cards = set(cards)
    cards.difference_update(IGNORE)
    cards = list(cards)
    cards.sort()
    d["cards"] = cards
    featurearray.append(d)

# print(featurearray)

vectorizer = DictVectorizer()
data = vectorizer.fit_transform(featurearray).toarray()
print(type(data))
print(data)

# https://github.com/scikit-learn/scikit-learn/blob/70cf4a676caa2d2dad2e3f6e4478d64bcb0506f7/examples/cluster/plot_hierarchical_clustering_dendrogram.py
def plot_dendrogram(model, **kwargs):
    # The number of observations contained in each cluster level
    no_of_observations = np.arange(2, model.children_.shape[0] + 2)
    # Create linkage matrix and then plot the dendrogram
    linkage_matrix = np.column_stack([model.children_, model.distances_, no_of_observations]).astype(float)
    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)
    return linkage_matrix


def label(i):
    if i < len(decks):
        return list(decks.keys())[i]
    return i


def color(i):
    return "white"


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


def clusterTree(data):
    N_CLUSTERS = 10
    clustering = AgglomerativeClustering(linkage="average", n_clusters=N_CLUSTERS, compute_distances=True, affinity="l1")
    clustering.fit(data)
    # plot_dendrogram(clustering, labels=clustering.labels_)
    linkage_matrix = plot_dendrogram(clustering, show_leaf_counts=False)
    print(linkage_matrix)
    showTree(linkage_matrix)
    # plt.show()


clusterTree(data)
