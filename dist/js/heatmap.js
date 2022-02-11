function drawHeatMap(id, f) {
	// set the dimensions and margins of the graph
	const margin = { top: 80, right: 25, bottom: 30, left: 40 },
		width = 1450 - margin.left - margin.right,
		height = 1450 - margin.top - margin.bottom;

	// append the svg object to the body of the page
	const svg = d3
		.select("#" + id)
		.append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", `translate(${margin.left}, ${margin.top})`);

	//Read the data
	d3.json("data/cards.json").then(function (data) {
		data = Object.values(data);
		creatures = data.filter((card) => "power" in card && !isNaN(card.power) && "toughness" in card && !isNaN(card.toughness));
		aggregate = [];
		for (let p = 0; p < 13; p++)
			for (let t = 0; t < 13; t++) {
				c = data.filter((card) => card.power == p && card.toughness == t);
				if (c.length === 0) continue;
				intensity = c.map(f).reduce((a,b)=>a+b);
				aggregate.push({
					power: p,
					toughness: t,
					intensity: intensity,
					names: c.map((card) => card.name).reduce((a, b) => a + ", " + b),
				});
			}
		console.log(aggregate);
		// Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
		const myGroups = Array.from(new Set(aggregate.map((d) => Number(d.power))));
		const numerically = (a, b) => a - b;
		myGroups.sort(numerically);
		const myVars = Array.from(new Set(aggregate.map((d) => Number(d.toughness))));
		myVars.sort(numerically);

		// Build X scales and axis:
		const x = d3.scaleBand().range([0, width]).domain(myGroups).padding(0.05);
		svg.append("g").style("font-size", 15).attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x).tickSize(0)).select(".domain").remove();

		// Build Y scales and axis:
		const y = d3.scaleBand().range([height, 0]).domain(myVars).padding(0.05);
		svg.append("g").style("font-size", 15).call(d3.axisLeft(y).tickSize(0)).select(".domain").remove();
		
		// Build color scale
		const max = Math.max(...aggregate.map(entry=>entry.intensity));
		const myColor = d3.scaleSequentialLog().interpolator(d3.interpolateYlOrRd).domain([1, max]);

		// create a tooltip
		const tooltip = d3
			.select("#" + id)
			.append("div")
			.style("opacity", 0)
			.attr("class", "tooltip")
			.style("background-color", "white")
			.style("border", "solid")
			.style("border-width", "2px")
			.style("border-radius", "5px")
			.style("padding", "5px");

		// Three function that change the tooltip when user hover / move / leave a cell
		const mouseover = function (event, d) {
			tooltip.style("opacity", 1);
			d3.select(this).style("stroke", "black").style("opacity", 1);
		};
		const mousemove = function (event, d) {
			tooltip
				.html(d.names+" "+Math.round(d.intensity*100)/100)
				.style("left", event.x / 2 + "px")
				.style("top", event.y / 2 + "px");
		};
		const mouseleave = function (event, d) {
			tooltip.style("opacity", 0);
			d3.select(this).style("stroke", "none").style("opacity", 0.8);
		};

		// add the squares
		svg
			.selectAll()
			.data(aggregate, function (d) {
				return d.power + ":" + d.toughness;
			})
			.join("rect")
			.attr("x", function (d) {
				return x(d.power);
			})
			.attr("y", function (d) {
				return y(d.toughness);
			})
			.attr("rx", 4)
			.attr("ry", 4)
			.attr("width", x.bandwidth())
			.attr("height", y.bandwidth())
			.style("fill", function (d) {
				return myColor(d.intensity);
			})
			.style("stroke-width", 4)
			.style("stroke", "none")
			.style("opacity", 0.8)
			.on("mouseover", mouseover)
			.on("mousemove", mousemove)
			.on("mouseleave", mouseleave);
	});

	// Add title to graph
	svg.append("text").attr("x", 0).attr("y", -50).attr("text-anchor", "left").style("font-size", "22px");//.text("Power and toughness combinations");

	// Add subtitle to graph
	svg
		.append("text")
		.attr("x", 0)
		.attr("y", -20)
		.attr("text-anchor", "left")
		.style("font-size", "14px")
		.style("fill", "grey")
		.style("max-width", 400);
		//.text("Power and thoughness values of creatures in the average deck.");
}
