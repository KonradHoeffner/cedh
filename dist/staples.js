function cardCount() {
	const cards = {};
	const notfound = new Set();
	for (const deckName in decks) {
		for (const cardName of decks[deckName]) {
			if (!cards[cardName]) {
				if (!mtgindex[cardName]) {
					notfound.add(cardName);
					continue;
				}
				cards[cardName] = mtgindex[cardName];
				cards[cardName].count = 0;
			}
			cards[cardName].count++;
		}
	}
	if (notfound.size > 0) console.warn("Not found in index: ", notfound);
	console.log(cards);
	return cards;
}
