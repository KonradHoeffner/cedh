const margin = { top: 30, right: 30, bottom: 30, left: 50 };
const width = 2460 - margin.left - margin.right;
const height = 1400 - margin.top - margin.bottom;

function count(id, attr, filter, color, scale) {
	// todo: remove attr
	// https://www.d3-graph-gallery.com/graph/density_slider.html
	const svg = d3Svg(id, margin, width, height);

	d3.json("data/cards.json").then(function (data) {
		data = Object.values(data);
		data = data.filter(filter);
		data = data.filter((card) => card.count > 0); // workaround for buggy cards with count=0 which breaks log scale visualization
		data.sort((a, b) => b.count - a.count);
		//const minX = Math.min(...data.map((card) => card[attr]));
		const minX = 1;
		// add the x Axis
		const x = d3.scaleLinear().domain([minX, data.length]).range([0, width]);
		svg.append("g").attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x));
		for (let i = 0; i < data.length; i++) {
			data[i].sortRank = i + 1;
		}
		data.push({ count: 1, sortRank: 1 }); // close the curve

		const y = scale.range([height, 0]).domain([1, Math.max(...data.map((card) => card.count))]);
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
					.curve(d3.curveCatmullRom)
					.x(function (d) {
						return x(d.sortRank);
					})
					.y(function (d) {
						return y(d.count);
					})
			);
	});
}
