window.onload = async function() {
    $('#view').css("color", "blue");
    await create_view()
};

run = 0;
let result;

let update_interval;

let values;

let svg;

let margin, width, height;



let i_dn = 0;
let i_ts = 0;
let times = null;

async function create_menu(parent) {

    result = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': run, 'filter': {'t': ['all_data', 'times']}});

    times = result.result.t;

    let i_times = [0, times.length-1];



    let margin = {left: 50, right: 250};
    let width = window.innerWidth - margin.left - margin.right;
    let height = 50;
    let x = d3.scaleLinear()
        .domain(i_times)
        .range([0, width])
        .clamp(true);

    let svg = parent.append("svg");

    let time_label = svg.append("text").attr('x', 45).attr('y', 70).text(new Date(times[0]*1E3));

    let slider = svg.append("g")
        .attr("class", "slider")
        .attr("transform", "translate(" + margin.left + "," + height / 2 + ")");

    slider.append("line")
        .attr("class", "track")
        .attr("x1", x.range()[0])
        .attr("x2", x.range()[1])
        .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "track-inset")
        .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "track-overlay")
        .call(d3.drag()
            .on("start drag", function() {
                let h = x.invert(d3.event.x);
                h = Math.round(h);
                handle.attr("cx", x(h));
                let t = times[h]*1000;
                time_label.text(new Date(t));

            })
            .on("end", async function() {
                let h = x.invert(d3.event.x);
                i_ts = Math.round(h);
                console.log(i_ts);
                await update_view()
            }));

    slider.insert("g", ".track-overlay")
        .attr("class", "ticks")
        .attr("transform", "translate(0," + 18 + ")")
        .selectAll("text")
        .data(x.ticks(i_times[1]/6))
        .enter().append("text")
        .attr("x", x)
        .attr("text-anchor", "middle")
        .text(function(d) { return d; });

    var handle = slider.insert("circle", ".track-overlay")
        .attr("class", "handle")
        .attr("r", 9);

    /*
    slider.transition() // Gratuitous intro!
        .duration(750)
        .tween("hue", function() {
            var i = d3.interpolate(0, 70);
            return function(t) { hue(i(t)); };
        });
     */

}




async function create_view(){



    margin = {top: 20, right: 50, bottom: 50, left: 50};
    width = window.innerWidth - margin.left - margin.right;
    height = d3.select('.diag').node().getBoundingClientRect().height - margin.top - margin.bottom;

    // set the ranges
    x = d3.scaleLinear().range([0, width]);
    y = d3.scaleLinear().range([height, 0]);

    // append the svg obgect to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    svg = d3.select(".diag").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    div = d3.select("body").append("div").attr("class", "tooltip");

    await update_view();
    await set_updater();

    await create_menu(d3.select(".menu"));
}

async function set_updater() {
    clearInterval(update_interval);
    update_interval = setInterval(await async function() {
        await update_view();
    }, 500*1000);
}

async function update_view(){
    let data = await get_data();

    // Scale the range of the data
    x.domain([0, d3.max(data.rect, function(d) { return d.p_j; })*1.05]);
    y.domain([0, (data.rect[data.rect.length-1].mc + data.rect[data.rect.length-1].dc)*1.05]);

    valueline = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.close); });

    svg.selectAll(".mo_rect").remove();

    let new_rects = svg.selectAll('.mo_rect').data(data.rect).enter();
    new_rects.append('rect')
        .classed('mo_rect', true).classed('mc', true)
        .attr('x', function(d){ return x(d.p_i); })
        .attr('y', function(d){ return y(d.mc); })
        .attr('width', function(d){ return x(d.p); })
        .attr('height', function(d){ return y(0)-y(d.mc); });
    new_rects.append('rect')
        .classed('mo_rect', true).classed('dc', true)
        .attr('x', function(d){ return x(d.p_i); })
        .attr('y', function(d){ return y(d.mc+d.dc); })
        .attr('width', function(d){ return x(d.p); })
        .attr('height', function(d){ return y(0)-y(d.dc); });
    svg.selectAll('.mo_rect').on("mouseover", function(d) {
        div.transition()
            .duration(200)
            .style("opacity", .9);
        div.html("Power plant: " + d.id + "<br/>Power: " + d.p.toFixed(2) + "<br/>Marginal costs: " + d.mc.toFixed(2) + "<br/>Distance costs: " + d.dc.toFixed(2))
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY-div.node().getBoundingClientRect().height) + "px");
    })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });

    svg.selectAll("line").remove();
    svg.append("line")
        .attr("x1", function () { return x(data.d)})
        .attr("x2", function () { return x(data.d)})
        .attr("y1", function () { return y(0)})
        .attr("y2", function () { return y(data.price)});
    svg.append("line")
        .attr("x1", function () { return x(data.d)})
        .attr("x2", function () { return x(0)})
        .attr("y1", function () { return y(data.price)})
        .attr("y2", function () { return y(data.price)});

    svg.selectAll("text").remove();
    svg.append('text')
        .text(function () { return "Market price: " + data.price.toFixed(2) + " CHF/MWh" })
        .attr('y', function () { return y(data.price)-5 })
        .attr('x', 5);


    // Add the X Axis
    svg.selectAll('.x_axis').remove();
    svg.append("g").classed('x_axis', true).call(d3.axisBottom(x))
        .attr("transform", "translate(0," + height + ")")
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // Add the Y Axis
    svg.selectAll('.y_axis').remove();
    svg.append("g").classed('y_axis', true).call(d3.axisLeft(y));
}

async function get_data(){


    result = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': run, 'filter': {
            'pp': ['all_data', 'power_plants', i_dn, i_ts],
            'dn_id': ['all_data', 'distribution_networks', i_dn],
            'd': ['all_data', 'demand', i_ts],
            'price': ['all_data', 'market_price', i_dn, i_ts]}});
    let pps = result.result.pp;

    let rect = [];
    for(let i = 0; i < pps.p.length; i++) {
        rect[i] = {};
        rect[i].id = pps.ids[i];
        rect[i].mc = pps.m_c[i];
        rect[i].dc = pps.d_c[i];
        rect[i].p = pps.p[i];
        if(i===0){
            rect[i].p_i = 0;
        } else {
            rect[i].p_i = rect[i-1].p_j;
        }
        rect[i].p_j = rect[i].p_i + rect[i].p
    }
    rect.colums = Object.keys(rect[0]);

    let data = {'rect': rect,
        'dn_id': result.result.dn_id,
        'd': result.result.d,
        'price': result.result.price};
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
        return JSON.parse(data);
    }
}

