# Magic the Gathering cEDH Database Analysis

## Docker
Docker gives you the easiest setup:

    docker build . -t mtgcompare
    docker run mtgcompare

## Requirements

* python
* pip

## Setup
You may want to use a virtual environment.

* `pip install -r requirements.txt`

## Run

## Algorithm

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

## Files

* main.py: execute this file to generate the decklist visualization
* correlation.py: execute this file to generate the card visualization
* crawler.py: slightly modified copy of the cEDH Decklist Database crawler from <https://anonymous.4open.science/r/cEDH-DDB-Crawler-D2E6>
* cards.json: card attributes like type and mana cost from Scryfall, generate using [mtgslides](https://github.com/konradHoeffner/mtgslides) and copy here
* links.json: generated file containing a JSON array of decklist links, mostly from moxfield
* cards.json: generated file containing a JSON object with decklist names as keys and an array of card names as values
* tree.pdf: generated file containing the visualization

## Dependencies on External Web Services

* <https://cedh-decklist-database.com>
* Thanks to <https://www.gerbrand.dev/> for providing a useful Moxfield API because Moxfield does not want to publish their own API and crawling their site with JavaScript is very time consuming and error prone.

## Future Work

* provide a Dockerfile
* publish the results as an interactive website
* colorize the visualization of cards
* use different distance functions
* use commander identity and card colors to calculate scores relative to the maximum value
* add graph not based on clustering but on distance cutoff
