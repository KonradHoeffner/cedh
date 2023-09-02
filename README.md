# Magic the Gathering cEDH Database Analysis

## Requirements

* python
* pip

## Setup
You may want to use a virtual environment.

* `pip install -r requirements.txt`

## Files

### py
* main.py: execute this file to generate the decklist visualization
* savedecks.py: execute this file to crawl and save the current decklists of the cEDH decklist database
* cardstats.py: execute this file after savedecks.py to generate and save the card stats
* correlation.py: execute this file to generate the card visualization
* crawler.py: slightly modified copy of the cEDH Decklist Database crawler from <https://anonymous.4open.science/r/cEDH-DDB-Crawler-D2E6>
* cards.json: card attributes like type and mana cost from Scryfall, generate using [mtgslides](https://github.com/konradHoeffner/mtgslides) and copy here
* <s>tree.pdf: generated file containing the visualization</s>

### dist
#### dist/data
These files are generated by executing scripts in the py folder above.

* `links.json`: Decklist links of the cEDH decklist database as a JSON array of decklist links, mostly from moxfield. Generated by `py/savedecks.py`.
* `decks.json` and `decks.js`: Decklists of the cEDH decklist database, Generated by `py/savedecks.py`.
* `cards.json` and `cards.js`: Card status of the cEDH decklist database. Generated by `py/cardstats.py` after `py/savedecks.py`

## GitHub Actions
`savedecks.py` and `cardstats.py` are [run daily in a GitHub workflow](https://github.com/KonradHoeffner/cedh/blob/master/.github/workflows/build.yml) and deployed to [data folder](https://github.com/KonradHoeffner/cedh/tree/gh-pages/data) of the [gh-pages branch](https://github.com/konradhoeffner/cedh/tree/gh-pages).

## Docker
If you want to generate the card visualization with `correlation.py` but don't want to install Python or the required libraries, you can use Docker as follows:

    docker build . -t mtgcompare
    docker run mtgcompare

## Dependencies on External Web Services

* <https://cedh-decklist-database.com>
* <https://www.moxfield.com> The moxfield API is inofficial and may break at any time.

## Monthly cEDH staples post 

This is how I generate the monthly cEDH staples posts at <https://reddit.com/r/cedh>, for example see [July 2022](https://www.reddit.com/r/CompetitiveEDH/comments/vowkns/july_2022_cedh_staples/).

	python py/savedecks.py
    python py/cardstats.py

Or download <https://github.com/KonradHoeffner/cedh/raw/gh-pages/data/cards.json> to `dist/data`.
Download the comparison file at that point in time from GitHub and save it to `dist/data/cards.old.json`.

    python py/diff.py > diff.txt

Per request, only use the top two sections, top increased and top decreased.

## Visualization Algorithm

1. if `links.json` does not exist:
	* fetch decklist links from the [Competitive EDH Decklist Database](https://cedh-decklist-database.com/) using a crawler based on <https://anonymous.4open.science/r/cEDH-DDB-Crawler-D2E6>
	* save the result in `links.json`
2. if `decks.json` does not exist then for each moxfield decklist link:
	* replace <https://www.moxfield.com/> with <https://www.gerbrand.dev/>
	* fetch the resulting URL
	* parse the content into a dictionary with decklist names as keys and lists of card names as values
	* save the result in `decks.json`
3. remove very common lands and mana rocks from the decks
4. transform the decks into binary vectors using a [DictVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.DictVectorizer.html)
5. perform [agglomerative clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html)
6. create the linkage matrix
7. [visualize the linkage matrix as a tree of labelled nodes](https://datascience.stackexchange.com/questions/101854/how-to-visualize-a-hierarchical-clustering-as-a-tree-of-labelled-nodes-in-python)


## Future Work

* use different distance functions
* use commander identity and card color relative scores in visualization
* add graph not based on clustering but on distance cutoff
