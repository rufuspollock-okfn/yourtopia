/* Data processing */
var time = Array(2001, 2003, 2006, 2031);
var min_year = d3.min(time);
var max_year = d3.max(time);

var column = Array(34,56,67,12);
var min_column = d3.min(column);
var max_column = d3.max(column)

/* Data processing END */

var data = d3.range(time.length).map(function(i) {
  return {x: time[i], y: column[i]};
});

var w = 450,
    h = 275,
    p = 20,
    x = d3.scale.linear().domain([min_year, max_year]).range([0, w]),
    y = d3.scale.linear().domain([min_column, max_column]).range([h, 0]);

var vis = d3.select("body")
    .data([data])
  .append("svg")
    .attr("width", w + p * 2)
    .attr("height", h + p * 2)
  .append("g")
    .attr("transform", "translate(" + p + "," + p + ")");

var rules = vis.selectAll("g.rule")
    .data(x.ticks(10))
  .enter().append("g")
    .attr("class", "rule");

rules.append("line")
    .attr("x1", x)
    .attr("x2", x)
    .attr("y1", 0)
    .attr("y2", h - 1);

rules.append("line")
    .attr("class", function(d) { return d ? null : "axis"; })
    .attr("y1", y)
    .attr("y2", y)
    .attr("x1", 0)
    .attr("x2", w + 1);

rules.append("text")
    .attr("x", x)
    .attr("y", h + 3)
    .attr("dy", ".71em")
    .attr("text-anchor", "middle")
    .text(x.tickFormat(10));

rules.append("text")
    .attr("y", y)
    .attr("x", -3)
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .text(y.tickFormat(10));

vis.append("path")
    .attr("class", "line")
    .attr("d", d3.svg.line()
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); }));

vis.selectAll("circle.line")
    .data(data)
  .enter().append("circle")
    .attr("class", "line")
    .attr("cx", function(d) { return x(d.x); })
    .attr("cy", function(d) { return y(d.y); })
    .attr("r", 3.5);
