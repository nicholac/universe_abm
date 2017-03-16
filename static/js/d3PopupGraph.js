
function bdGram(layer, d3Elem) {

	//console.log(JSON.stringify(layer.feature.treeJson));

	var margin = {top: 50, right: 50, bottom: 50, left: 50},
		width = 300 - margin.left - margin.right,
		height = 200 - margin.top - margin.bottom;

	var color = d3.scale.category20c();

	var treemap = d3.layout.treemap()
	    .size([width, height])
	    .sticky(true)
	    .value(function(d) { return d.size; });

	var svg = d3.select(d3Elem).append("svg-d3");

	svg .attr("width", width)
	    .attr("height", height)
	    .style("left", 2 + "px")
	    .style("top", 2 + "px");

	//Set Root Data from layer json
	root = layer.feature.properties.treeJson

	  var node = svg.datum(root).selectAll(".node")
	      .data(treemap.nodes)
	    .enter().append("svg")
	      .attr("class", "node")
	      .call(position)
	      .style("background", function(d) { return d.children ? color(d.name) : null; })
	      .text(function(d) { return d.children ? null : d.name; });

	  d3.selectAll("input").on("change", function change() {
	    var value = this.value === "count"
	        ? function() { return 1; }
	        : function(d) { return d.size; };

	    node
	        .data(treemap.value(value).nodes)
	      	.transition()
	        .duration(1500)
	        .call(position);
	  });


	function position() {
	  this.style("left", function(d) { return d.x + "px"; })
	      .style("top", function(d) { return d.y + "px"; })
	      .style("width", function(d) { return Math.max(0, d.dx - 1) + "px"; })
	      .style("height", function(d) { return Math.max(0, d.dy - 1) + "px"; });
	}
};
