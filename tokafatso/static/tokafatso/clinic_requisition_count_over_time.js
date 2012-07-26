var margin = {top: 20, right: 0, bottom: 10, left: 10},
    width = 150,
    height = 60,
    baseline = 80;

var data = {{ data }},
    labels = ['past 12 weeks', 'last week', 'this week']

var x = d3.scale.linear().domain([0,d3.max(data)*1.2]).range([0,width-baseline-15]);

var svg = d3.select("#count-{{ clinic.id }}")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .style("margin-left", -margin.left + "px")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var rect = svg.selectAll("rect")
        .data(data)
    .enter().append("rect")
        .attr("y", function(d, i) {return i * 20;})
        .attr("x", baseline)
        .attr("width", x)
        .attr("height", 20)
        .attr("stroke", "white")
        .attr("fill", "steelblue")

var labels = svg.selectAll(".labels")
        .data(labels)
    .enter().append("text")
        .attr("class", "labels")
        .text(function(d) {return d;})
        .attr("text-anchor", "end")
        .attr("y", function(d, i) {return i * 20 + 13;})
        .attr("x", baseline-2)
        .attr("font-family", "sans-serif")
        .attr("font-size", "11px")
        .attr("fill", "gray");

var text = svg.selectAll(".text")
        .data(data)
    .enter().append("text")
        .attr("class", "text")
        .text(function(d) {return d;})
        .attr("text-anchor", "start")
        .attr("y", function(d, i) {return i * 20 + 13;})
        .attr("x", function(d, i) {return baseline+x(d)+2;})
        .attr("font-family", "sans-serif")
        .attr("font-size", "11px")
        .attr("fill", "gray");