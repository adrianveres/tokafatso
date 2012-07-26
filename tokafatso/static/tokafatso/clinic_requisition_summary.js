function plot_clinic_requisition_summary(clinic_json) {

    var clinic = JSON.parse(clinic_json);

    var margin = {top: 5, right: 5, bottom: 5, left: 5},
        width = 200,
        height = 60,
        baseline = 80;

    var labels = ['past 12 weeks', 'last week', 'this week'],
        units = ['/week','',''],
        barcolors = ['lightgray','lightsteelblue','steelblue']

    var x = d3.scale.linear().domain([0,d3.max(clinic['data'])*1.2]).range([2,width-baseline-35]);

    var svg = d3.select("#"+clinic["clinic_id"])
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .style("margin-left", margin.left + "px")

    var rect = svg.selectAll("rect")
            .data(clinic['data'])
        .enter().append("rect")
            .attr("y", function(d, i) {return i * 20;})
            .attr("x", baseline)
            .attr("width", x)
            .attr("height", 20)
            .attr("stroke", "white")
            .attr("fill", function(d, i) {return barcolors[i];})

    var labels = svg.selectAll(".labels")
            .data(labels)
        .enter().append("text")
            .attr("class", "labels")
            .text(function(d) {return d;})
            .attr("text-anchor", "end")
            .attr("y", function(d, i) {return i * 20 + 14;})
            .attr("x", baseline-5)
            .attr("font-family", "sans-serif")
            .attr("font-size", "11px")
            .attr("fill", "gray");

    var text = svg.selectAll(".text")
            .data(clinic['data'])
        .enter().append("text")
            .attr("class", "text")
            .text(function(d, i) {return d+units[i];})
            .attr("text-anchor", "start")
            .attr("y", function(d, i) {return i * 20 + 14;})
            .attr("x", function(d, i) {return baseline+x(d)+5;})
            .attr("font-family", "sans-serif")
            .attr("font-size", "11px")
            .attr("fill", "gray");
};


function plot_clinic_data_timeseries(clinic_json) {

var clinic = JSON.parse(clinic_json);

var n = 40,
    random = d3.random.normal(0, .2),
    data0 = d3.range(n).map(random);
    data1 = d3.range(n).map(random);

var margin = {top: 10, right: 10, bottom: 20, left: 40},
    width = 960 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

//Change the data format to fit the d3 'model'.
dataseries = []
django.jQuery.each(clinic['data_headers'], function(headerIndex, header){
    dataseries[headerIndex] = [];
});

django.jQuery.each(clinic['data'], function(weekIndex, week){
    django.jQuery.each(clinic['data_headers'], function(headerIndex, header){
        dataseries[headerIndex][weekIndex] = {x:weekIndex, y:week[header], y0:0};
    });
});

var totals = [];
django.jQuery.each(dataseries[dataseries.length-1], function(index, value) {
    totals[index] = value.y + value.y0;
});

var x = d3.scale.linear()
    .domain([0, dataseries[0].length])
    .range([0, width]);

var ylim = d3.max(totals);

var y = d3.scale.linear()
    .domain([0, 40])
    .range([height, 0]);

console.log(ylim);

var line = d3.svg.line()
    // .interpolate("basis")
    .x(function(d,i) { return x(i); })
    .y(function(d) { return y(d.y + d.y0); })

var svg = d3.select("#"+clinic["clinic_id"])
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var stack = d3.layout.stack()
    // .values(function(d) {return series[d.name];})

var path = svg.append("g")
  .selectAll(".line")
    .data(stack(dataseries))
  .enter().append("path") 
    .attr("class", "line")
    .attr("d", line)
    .style("fill","none")
    .style("stroke","#000");

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.svg.axis().scale(x).orient("bottom"));

svg.append("g")
    .attr("class", "y axis")
    .call(d3.svg.axis().scale(y).orient("left"));

}


function plot_clinic_requisition_timeseries(clinic_json) {

var clinic = JSON.parse(clinic_json);

var n = 40,
    random = d3.random.normal(0, .2),
    data0 = d3.range(n).map(random);
    data1 = d3.range(n).map(random);

var margin = {top: 10, right: 10, bottom: 20, left: 40},
    width = 960 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

//Change the data format to fit the d3 'model'.
var timeseries = [].
    dataseries = [];

django.jQuery.each(clinic['data'], function(weekIndex, week){
    timeseries[weekIndex] = week['startdate'];
    dataseries[weekIndex] = week['count']; 
});

var x = d3.scale.linear()
    .domain([0, dataseries.length])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([0, d3.max(dataseries)])
    .range([height, 0]);

console.log(dataseries);

var line = d3.svg.line()
    // .interpolate("basis")
    .x(function(d,i) {return x(i); })
    .y(function(d) { return y(d); });

var svg = d3.select("#"+clinic["clinic_id"])
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var path = svg.append("g")
  .selectAll(".line")
    .data([dataseries])
  .enter().append("path") 
    .attr("class", "line")
    .attr("d", line)
    .style("fill","none")
    .style("stroke","#f00");

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.svg.axis().scale(x).orient("bottom"));

svg.append("g")
    .attr("class", "y axis")
    .call(d3.svg.axis().scale(y).orient("left"));

}


