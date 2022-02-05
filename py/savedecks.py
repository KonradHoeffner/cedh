from crawler import Crawler
from urllib.request import urlopen, Request, HTTPError
import json
from pathlib import Path
import re
import sys

LINKFILE = "./dist/links.json"
try:
    url = "https://cedh-decklist-database.com/"
    crawler = Crawler(url)
    crawler.run()
    print(len(crawler.links), "crawled links")
    links = crawler.links
    with open(LINKFILE, "w") as f:
        json.dump(links, f, indent=2)
except Exception:
    if Path(LINKFILE).exists():
        with open(LINKFILE, "r") as f:
            links = json.load(f)
            print(
                "Error crawling",
                url,
                len(links),
                "links loaded from existing linkfile",
                LINKFILE,
            )
    else:
        print("Error crawling " + url + " and no existing linkfile. Aborting.")
        raise

PREFIX = "https://www.moxfield.com/decks/"
REPLACEMENT = "https://api.moxfield.com/v2/decks/all/"


def crawlDecks(links):
    decks = dict()
    for link in links:
        if not PREFIX in link:
            continue
        url = link.replace(PREFIX, REPLACEMENT)
        try:
            fakeHeaders = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
            }
            req = Request(url, headers=fakeHeaders)
            text = urlopen(req).read().decode("utf-8")
            j = json.loads(text)
        except HTTPError:
            print("Could not open", url)
            # raise # when debugging
            continue
        # print(text)
        title = j["name"]
        title = title.encode("ascii", "ignore").decode()
        print(title, url)
        commanders = list(j["commanders"].keys())
        commanders.sort()
        mainboard = list(j["mainboard"].keys())
        mainboard.sort()  # smaller diffs in Git
        decks[title] = {"mainboard": mainboard, "commanders": commanders}
        # print(cards)
    return decks


DECKFILE = "./dist/decks.json"
DECKFILE_ERROR = "./dist/decks_error.json"
DECKFILE_JS = "./dist/decks.js"
decks = crawlDecks(links)
MIN_DECKS = 250
size = len(decks)

if size < MIN_DECKS:
    with open(DECKFILE_ERROR, "w") as f:
        json.dump(decks, f, indent=2)
        print("Less than", MIN_DECKS, "decks. Something probably went wrong, aborting. Saved", size, "decks in", DECKFILE_ERROR)
    sys.exit(1)

with open(DECKFILE, "w") as f:
    json.dump(decks, f, indent=2)
    print()
    print("Saved", size, "crawled decks in", DECKFILE)
json_string = json.dumps(decks, indent=2)
with open(DECKFILE_JS, "w") as f_js:
    f_js.write("const decks =\n" + json_string + ";")
    print("Saved", DECKFILE_JS)
