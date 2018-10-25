let run = 0;
let diag;
let update_speed = 0.2;
let update_interval_time = 1;
let update_interval;


window.onload = async function() {

    // $('#view').css("color", "blue");

    // Diagram
    //let d3d = d3.select("body");
    let d3d = d3.select("#view");
    d3d.style("color", "blue");

    diag = new Diagram(d3d);

    await updateAll(0);


    await set_updater()
};

async function updateAll(updateSpeed) {
    await diag.updateData();
    diag.updateView(updateSpeed);
}

async function set_updater() {
    clearInterval(update_interval);
    update_interval = setInterval(await async function() {
        await updateAll(update_speed*1000);
    }, update_interval_time * 1000);
}

async function get(data_dict){
    let query_name = 'get_mu_results';
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


d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};

// // // //

/*
window.onload = async function() {
    $('#view').css("color", "blue");
    await create_view()
};

let result;
let times;
let datetimes = [];
let values;
let valueline,x, y, div, formatTime;



async function create_view(){

    let data = await get_data();

    // Add the valueline path.
    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);

    await update_view();
    await set_updater();
}



async function update_view(){
    let data = await get_data();

        // Scale the range of the data
    //x.domain(d3.extent(data, function(d) { return d.time; }));
    //y.domain(d3.extent(data, function(d) { return d.value; }));

    //valueline = d3.line()
    //    .x(function(d) { return x(d.date); })
    //    .y(function(d) { return y(d.close); });



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
    data = result.data_histfore;

    // Time format
     for (i = 0; i < data.forecast.time.length; i++) {
        datetimes[i] = new Date(data.forecast.time[i] * 1E3);
        data.forecast.time[i] = datetimes[i]
    }
     for (i = 0; i < data.historic.time.length; i++) {
        datetimes[i] = new Date(data.historic.time[i] * 1E3);
        data.historic.time[i] = datetimes[i]
    }

    if (data) {
        data = Object.keys(data_x).map(function (c, id_c) {
            return {id: Object.keys(data_x)[id_c]}
        });
    }

    this.data.data_formatted = data

}
*/