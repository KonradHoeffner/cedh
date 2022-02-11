let gridOptions;

function createTable() {
	const table = document.getElementById("staplesTable");

	const keys = ["count", "percent", "supercent", "rank", "superrank","identity_rank", "cmc", "colors", "color_identity"];

	const columnDefs = [
		{ field: "name", sortable: true, filter: "agTextColumnFilter" },
		{ field: "count", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "percent", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "rank", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "supercent", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "superrank", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "identity_rank", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "cmc", sortable: true, filter: "agNumberColumnFilter" },
		{ field: "colors", sortable: true, filter: "agSetColumnFilter" },
		{ field: "color_identity", sortable: true, filter: "agSetColumnFilter" },
	];

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
