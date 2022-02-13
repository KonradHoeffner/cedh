const margin = { top: 30, right: 30, bottom: 30, left: 50 };
const width = 2460 - margin.left - margin.right;
const height = 1400 - margin.top - margin.bottom;

function count(id, attr, filter, color) {
	// https://www.d3-graph-gallery.com/graph/density_slider.html
	const svg = d3Svg(id, margin, width, height);

	d3.json("data/cards.json").then(function (data) {
		data = Object.values(data);
		data = data.filter(filter);
		data.sort((a, b) => a[attr] - b[attr]);
		const minX = Math.min(...data.map((card) => card[attr]));
		// add the x Axis
		const x = d3.scaleLinear().domain([minX, data.length]).range([0, width]);
		svg.append("g").attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x));
		data.push({ count: 0, [attr]: minX }); // to close the curve
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
			.attr("fill", color)
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
						return x(d[attr]);
					})
					.y(function (d) {
						return y(d.count);
					})
			);
	});
}
