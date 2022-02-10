const margin = { top: 30, right: 30, bottom: 30, left: 50 };
const width = 2460 - margin.left - margin.right;
const height = 1400 - margin.top - margin.bottom;

function drawHistogram(id, f) {
	// set the dimensions and margins of the graph

	// append the svg object to the body of the page
	const svg = d3
		.select("#" + id)
		.append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", `translate(${margin.left},${margin.top})`);

	// get the data
	d3.json("data/cards.json").then(function (data) {
		cmcs = Object.values(data).map(f);

		// add the x Axis
		const x = d3.scaleLinear().domain([0, 17]).range([0, width]);
		svg.append("g").attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x));

		var histogram = d3
			.histogram()
			.value(function (d) {
				return d;
			}) // I need to give the vector of value
			.domain(x.domain()) // then the domain of the graphic
			.thresholds(x.ticks(17)); // then the numbers of bins

		// And apply this function to data to get the bins
		var bins = histogram(cmcs);

		// Y axis: scale and draw:
		var y = d3.scaleLinear().range([height, 0]);
		y.domain([
			0,
			d3.max(bins, function (d) {
				return d.length;
			}),
		]); // d3.hist has to be called before the Y axis obviously
		svg.append("g").call(d3.axisLeft(y));

		// append the bar rectangles to the svg element
		svg
			.selectAll("rect")
			.data(bins)
			.enter()
			.append("rect")
			.attr("x", 1)
			.attr("transform", function (d) {
				return "translate(" + x(d.x0) + "," + y(d.length) + ")";
			})
			.attr("width", function (d) {
				return x(d.x1) - x(d.x0) - 1;
			})
			.attr("height", function (d) {
				return height - y(d.length);
			})
			.style("fill", "#69b3a2");
	});
}

function drawBarPlot(id, f) {
	// append the svg object to the body of the page
	const svg = d3
		.select("#" + id)
		.append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", `translate(${margin.left},${margin.top})`);

	// Parse the Data
	d3.json("data/cards.json").then(function (data) {
		data = Object.values(data);
		const cmcs = [];
		for (let i = 0; i < 17; i++) {
			cmcs.push({ cmc: i, count: 0 });
		}
		for (card of data) {
			cmcs[card.cmc].count += f(card);
		}
		console.log(cmcs);

		// X axis
		const x = d3
			.scaleBand()
			.range([0, width])
			.domain(cmcs.map((d) => d.cmc))
			.padding(0.2);
		svg
			.append("g")
			.text("CMC")
			.attr("transform", `translate(0, ${height})`)
			.call(d3.axisBottom(x))
			.selectAll("text")
			.attr("transform", "translate(-10,0)rotate(-45)")
			.style("text-anchor", "end");

		// Add Y axis
		const y = d3
			.scaleLinear()
			.domain([0, Math.max(...cmcs.map((x) => x.count))])
			.range([height, 0]);
		svg.append("g").call(d3.axisLeft(y));

		// Bars
		svg
			.selectAll("mybar")
			.data(cmcs)
			.join("rect")
			.attr("x", (d) => x(d.cmc))
			.attr("y", (d) => y(d.count))
			.attr("width", x.bandwidth())
			.attr("height", (d) => height - y(d.count))
			.attr("fill", "#69b3a2");
	});
}
