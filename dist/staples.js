function countCards() {
	const cards = {};
	const notfound = new Set();
	identityCount = {};

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
	// percentages
	for (const cardName in cards) {
		const card = cards[cardName];
		cards[cardName].percent = Math.round((100 * card.count) / Object.keys(decks).length);
	}
	if (notfound.size > 0) console.warn("Not found in index: ", notfound);
	//console.log(cards);
	return cards;
}

let gridOptions;

function createTable() {
	const table = document.getElementById("staplesTable");

	const keys = ["count", "percent", "cmc", "colors", "color_identity"];

	const columnDefs = [
		{ field: "name", sortable: true, filter: "agTextColumnFilter" },
		{ field: "count", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "percent", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "cmc", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "colors", sortable: true, filter: "agSetColumnFilter" },
		{ field: "color_identity", sortable: true, filter: "agSetColumnFilter" },
	];

	const cards = countCards();
	const rowData = [];
	for (const cardName in cards) {
		const card = cards[cardName];
		const entry = { name: cardName };
		rowData.push(entry);
		for (const key of keys) {
			entry[key] = card[key];
		}
	}
	const defaultColDef = { sortable: true, resizable: true };
	gridOptions = { columnDefs, rowData, defaultColDef, enableCellTextSelection: true };
	const gridDiv = document.getElementById("staplesGrid");
	new agGrid.Grid(gridDiv, gridOptions);
}

function exportCsv() {
	gridOptions.api.exportDataAsCsv();
}
