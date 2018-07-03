class MeritOrderDiagram {
    constructor(parent) {
        this.run = 0;

        this.div = parent.append("div").attr("class", "tooltip");

        this.margin = {top: 20, right: 50, bottom: 50, left: 50};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // set the ranges
        this.x = d3.scaleLinear().range([0, this.width]);
        this.y = d3.scaleLinear().range([this.height, 0]);

        // append the svg obgect to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g").attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");
    }

    async update(){
        let obj = this;
        let data = await this.get_data();

        if (data){

            // Scale the range of the data
            this.x.domain([0, d3.max(data.rect, function(d) { return d.p_j; })*1.05]);
            this.y.domain([0, (data.rect[data.rect.length-1].mc + data.rect[data.rect.length-1].dc)*1.05]);
            let svg = this.svg;

            svg.selectAll(".powerplant").remove();

            let powerplant = svg.selectAll('.powerplant').data(data.rect).enter().append('g').classed('powerplant', true);
            powerplant.append('rect')
                .classed('mo_rect', true).classed('mc', true)
                .attr('x', function(d){ return obj.x(d.p_i); })
                .attr('y', function(d){ return obj.y(d.mc); })
                .attr('width', function(d){ return obj.x(d.p); })
                .attr('height', function(d){ return obj.y(0) - obj.y(d.mc); });
            powerplant.append('rect')
                .classed('mo_rect', true).classed('dc', true)
                .attr('x', function(d){ return obj.x(d.p_i); })
                .attr('y', function(d){ return obj.y(d.mc+d.dc); })
                .attr('width', function(d){ return obj.x(d.p); })
                .attr('height', function(d){ return obj.y(0) - obj.y(d.dc); });
            powerplant.on("mouseover", function(d) {
                let div = obj.div;

                let html = "Power plant: " + d.id;
                html += "<br/>Power: " + d.p.toFixed(2);
                html += "<br/>Marginal costs: " + d.mc.toFixed(2);
                html += "<br/>Distance costs: " + d.dc.toFixed(2);
                let top = d3.event.pageY - d3.event.offsetY + obj.y(d.dc + d.mc);
                top += obj.margin.top - div.node().getBoundingClientRect().height - 20;
                let left = d3.event.pageX - d3.event.offsetX + obj.x(d.p_i);
                left += obj.x(d.p) / 2 + obj.margin.left - div.node().getBoundingClientRect().width / 2;

                div.html(html).style("left", left + "px").style("top", top + "px");
                div.transition().duration(200).style("opacity", .9);
            })
                .on("mouseout", function(d) {
                    obj.div.transition()
                        .duration(500)
                        .style("opacity", 0);
                });

            svg.selectAll("line").remove();
            svg.append("line")
                .attr("x1", function () { return obj.x(data.d)})
                .attr("x2", function () { return obj.x(data.d)})
                .attr("y1", function () { return obj.y(0)})
                .attr("y2", function () { return obj.y(data.price)});
            svg.append("line")
                .attr("x1", function () { return obj.x(data.d)})
                .attr("x2", function () { return obj.x(0)})
                .attr("y1", function () { return obj.y(data.price)})
                .attr("y2", function () { return obj.y(data.price)});

            svg.selectAll("text").remove();
            svg.append('text')
                .text(function () { return "Market price: " + data.price.toFixed(2) + " CHF/MWh" })
                .attr('y', function () { return obj.y(data.price)-5 })
                .attr('x', 5);


            // Add the X Axis
            svg.selectAll('.x_axis').remove();
            svg.append("g").classed('x_axis', true).call(d3.axisBottom(obj.x))
                .attr("transform", "translate(0," + obj.height + ")")
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", "rotate(-65)");

            // Add the Y Axis
            svg.selectAll('.y_axis').remove();
            svg.append("g").classed('y_axis', true).call(d3.axisLeft(obj.y));

        }
    }



    async get_data(){
        let data = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': this.run, 'filter': {
                'pp': ['all_data', 'power_plants', i_dn, i_ts],
                'dn_id': ['all_data', 'distribution_networks', i_dn],
                'd': ['all_data', 'demand', i_ts],
                'price': ['all_data', 'market_price', i_dn, i_ts]}});
        if (data){
            this.run = data.run;
            let result = data.result;
            let pps = result.pp;

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

            data = {'rect': rect,
                'dn_id': result.dn_id,
                'd': result.d,
                'price': result.price};
        }
        return data
    }

}