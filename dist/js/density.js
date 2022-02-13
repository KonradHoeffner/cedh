const margin = { top: 30, right: 30, bottom: 30, left: 50 };
const width = 2460 - margin.left - margin.right;
const height = 1400 - margin.top - margin.bottom;

function count(id) {
	// https://www.d3-graph-gallery.com/graph/density_slider.html
	const svg = d3Svg(id, margin, width, height);

	d3.json("data/cards.json").then(function (data) {
		data = Object.values(data);
		data.sort((a, b) => a.rank - b.rank);
		data.push({ count: 0, rank: 0 }); // to close the curve
		console.log(data);
		// add the x Axis
		const x = d3.scaleLinear().domain([0, data.length]).range([0, width]);
		svg.append("g").attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x));

		// add the y Axis
		const y = d3
			.scaleLinear()
			.range([height, 0])
			.domain([0, Math.max(...data.map((card) => card.count))]);
		svg.append("g").call(d3.axisLeft(y));

		// Plot the area
		const curve = svg
			.append("g")
			.append("path")
			//.attr("class", "mypath")
			.datum(data)
			.attr("fill", "#69b3a2")
			.attr("opacity", ".8")
			.attr("stroke", "#000")
			.attr("stroke-width", 1)
			.attr("stroke-linejoin", "round")
			.attr(
				"d",
				d3
					.line()
					.curve(d3.curveBasis)
					.x(function (d) {
						return x(d.rank);
					})
					.y(function (d) {
						return y(d.count);
					})
			);
	});
}
