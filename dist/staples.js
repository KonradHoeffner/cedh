function countCards() {
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

function createTable()
{
	const table = document.getElementById("staplesTable");
	const keys = ["count","cmc","colors","color_identity"];
	
	const cards = countCards();
	for(const cardName in cards)
	{
		const card = cards[cardName];
		const row = table.insertRow();
		const nameCell = row.insertCell();
		nameCell.innerHTML = cardName;
		for(const key of keys)
		{
			const cell = row.insertCell();
			cell.innerHTML = card[key];
		}
	}
	const dataTable = new simpleDatatables.DataTable(table, {
		searchable: true
	});
}

