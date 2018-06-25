window.onload = async function() {
    $('#view').css("color", "blue");
    await create_view()
};

run = 0;
let result;

let update_interval;

let times;
let datetimes = [];
let values;

let svg;
let valueline,x, y, div, formatTime;

let margin, width, height;

async function create_view(){


    margin = {top: 20, right: 20, bottom: 90, left: 50};
    width = window.innerWidth - margin.left - margin.right;
    height = window.innerWidth/16*9 - margin.top - margin.bottom;

// set the ranges
    x = d3.scaleTime().range([0, width]);
    y = d3.scaleLinear().range([height, 0]);



// append the svg obgect to the body of the page
// appends a 'group' element to 'svg'
// moves the 'group' element to the top left margin
    svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);


    let data = await get_data();




    // Add the valueline path.
    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);



    formatTime = d3.timeFormat("%Y-%m-%d %H:%M:%S");

    // Add the scatterplot




    await set_updater();
}

async function set_updater() {
    clearInterval(update_interval);
    update_interval = setInterval(await async function() {
        await update_view();
    }, 5*1000);
}

async function update_view(){
    let data = await get_data();

        // Scale the range of the data
    x.domain(d3.extent(data, function(d) { return d.date; }));
    y.domain(d3.extent(data, function(d) { return d.close; }));

    valueline = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.close); });



    svg.select('.line').data([data]).attr("d", valueline);

    svg.selectAll("circle").remove();
    svg.selectAll("dot")
        .data(data)
        .enter().append("circle")
        .attr("r", 3)
        .attr("cx", function(d) { return x(d.date); })
        .attr("cy", function(d) { return y(d.close); })
        .attr("title", function (d) {
            return "Hallo";
        })
        .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div.html(formatTime(d.date) + "<br/>"  + d.close)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });

    // Add the X Axis
    svg.selectAll('.x_axis').remove();
    svg.append("g").classed('x_axis', true)
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickFormat(formatTime))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // Add the Y Axis
    svg.selectAll('.y_axis').remove();
    svg.append("g").classed('y_axis', true)
        .call(d3.axisLeft(y));
}



async function get_data(){
    result = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': run});
    result = JSON.parse(result);
    result = result.result;

    times = result.times;

    for (i = 0; i < times.length; i++) {
        datetimes[i] = new Date(times[i] * 1E3)
    }
    values = result.values;

    let data = [];
    for (i = 0; i < times.length; i++) {
        data[i] = {};
        data[i].date = datetimes[i];
        data[i].close = values[i];
    }
    data.colums = Object.keys(data[0]);
    return data
}




async function get(query_name, data_dict){
    let data = await $.get("/websimgui", {
        'fnc': query_name,
        'data': JSON.stringify(data_dict)});
    if (data === "false"){
        alert('GET request returned "false", check the request for the query "' + query_name + '"!');
        return false
    } else {
        return data;
    }
}

