class MeritOrderDiagram {
    constructor(parent) {
        this.run = 0;

        this.power_units = {'W': 1E0,'kW': 1E3,'MW': 1E6,'GW': 1E9,'TW': 1E12};
        this.power_unit = 'GW';
        //this.cost_units = {'E_J': 1E0,'E_kWh': 1/3.6E6,'E_MWh': 1/3.6E3};
        this.cost_units = {'E_J': 1E0,'E_kWh': 1/3.6E6,'E_MWh': 1/3.6E9};
        this.cost_unit = 'E_MWh';

        this.data = null;

        this.div = parent.append("div").attr("class", "tooltip");

        this.margin = {top: 20, right: 50, bottom: 70, left: 70};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // set the ranges
        this.xScale = d3.scaleLinear().range([0, this.width]);
        this.yScale = d3.scaleLinear().range([this.height, 0]);

        // append the svg obgect to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g").attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        this.priceLine = this.svg.append("line");
        this.demandLine = this.svg.append("line");
        this.priceText= this.svg.append('text');

        // add axis
        this.xAxis = this.svg.append("g")
            .classed('x_axis', true)
            .attr("transform", "translate(0," + this.height + ")");

        this.yAxis = this.svg.append("g")
            .classed('y_axis', true);

        this.xLabel = this.createXLabel(this.svg);
        this.yLabel = this.createYLabel(this.svg);

    }

    async updateView(updateSpeed){
        let obj = this;
        let data = this.data;

        if (data){

            // Scale the range of the data
            this.xScale.domain([0, d3.max(data.rect, function(d) { return d.p_j; })*1.05]);
            this.yScale.domain([0, d3.max(data.rect, function(d) { return d.tc;  })*1.05]);
            let svg = this.svg;

            let powerplant = svg.selectAll('.powerplant').data(data.rect);

            powerplant.exit().remove();

            let new_powerplant = powerplant.enter().append('g').classed('powerplant', true).moveToBack();

            new_powerplant.append('rect')
                .classed('mo_rect', true).classed('mc', true);

            new_powerplant.append('rect')
                .classed('mo_rect', true).classed('dc', true);
            new_powerplant.on("mouseover", function(d) {
                let div = obj.div;
                let html = "Power plant: " + d.id;
                html += "<br/>Info: " + d.info;
                html += "<br/>Power: " + d.p.toFixed(2);
                html += "<br/>Marginal costs: " + d.mc.toFixed(2);
                html += "<br/>Distance costs: " + d.dc.toFixed(2);
                let top = d3.event.pageY - d3.event.offsetY + obj.yScale(d.dc + d.mc);
                top += obj.margin.top - div.node().getBoundingClientRect().height - 20;
                let left = d3.event.pageX - d3.event.offsetX + obj.xScale(d.p_i);
                left += obj.xScale(d.p) / 2 + obj.margin.left - div.node().getBoundingClientRect().width / 2;

                div.html(html).style("left", left + "px").style("top", top + "px");
                div.transition().duration(200).style("opacity", .9);
            })
                .on("mouseout", function(d) {
                    obj.div.transition()
                        .duration(500)
                        .style("opacity", 0);
                });

            // update all
            powerplant = svg.selectAll('.powerplant');
            powerplant.select('.mc')
                .transition().duration(updateSpeed)
                .attr('x', function(d){ return obj.xScale(d.p_i); })
                .attr('y', function(d){ return obj.yScale(d.mc); })
                .attr('width', function(d){ return obj.xScale(d.p); })
                .attr('height', function(d){ return obj.yScale(0) - obj.yScale(d.mc); });
            powerplant.select('.dc').moveToBack()
                .transition().duration(updateSpeed)
                .attr('x', function(d){ return obj.xScale(d.p_i); })
                .attr('y', function(d){ return obj.yScale(d.mc+d.dc); })
                .attr('width', function(d){ return obj.xScale(d.p); })
                .attr('height', function(d){ return obj.yScale(0) - obj.yScale(d.dc); });



            this.demandLine
                .transition().duration(updateSpeed)
                .attr("x1", function () { return obj.xScale(data.demand)})
                .attr("x2", function () { return obj.xScale(data.demand)})
                .attr("y1", function () { return obj.yScale(0)})
                .attr("y2", function () { return obj.yScale(data.price)});
            this.priceLine
                .transition().duration(updateSpeed)
                .attr("x1", function () { return obj.xScale(data.demand)})
                .attr("x2", function () { return obj.xScale(0)})
                .attr("y1", function () { return obj.yScale(data.price)})
                .attr("y2", function () { return obj.yScale(data.price)});

            this.priceText
                .transition().duration(updateSpeed)
                .text(function () { return "Market price: " + data.price.toFixed(2) + " €/MWh" }) //text('Power ['+this.power_unit+']') // TODO Anpassen der units analog power
                .attr('y', function () { return obj.yScale(data.price)-5 })
                .attr('x', 5);


            // update axis
            this.xAxis
                .transition().duration(updateSpeed)
                .call(d3.axisBottom(this.xScale))
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", "rotate(-65)");

            this.yAxis
                .transition().duration(updateSpeed)
                .call(d3.axisLeft(this.yScale));

            this.updateXLabel(updateSpeed);
        }
    }

    createXLabel(parent){
        return parent.append("text").attr('class', 'xLabel');
    }
    async updateXLabel(updateSpeed){
        let obj = this;
        this.xLabel
            .transition().duration(updateSpeed)
            .text('Power ['+this.power_unit+']')
            .attr("transform", function() { return "translate(" + obj.xScale(obj.xScale.domain()[1]/2) + "," + obj.yScale(0-obj.yScale.domain()[1]/9) + ")"; });
    }

    createYLabel(parent){
        return parent.append("text")
            .text('Marginal Costs + Distance Costs [€/MWh]')
            .attr('class', 'yLabel')
            .attr("transform", "rotate(-90)")
            .style("text-anchor", "end")
            .attr("y", -35);
    }



    async updateData(){
        let filter = {
            'pp_ids': ['sorted_pp_id', 'pp_ids', i_dn],
            'pp': ['power_plants2'],
            'price': ['market_prices', 'prices', i_dn, i_ts],
            'demand': ['demands2']};
        let data = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter});
        if (data){
            this.run = data.run;
            let result = data.result;
            let pps = result.pp;
            let pp_ids = result.pp_ids;

            let rect = [];
            for(let i = 0; i < pp_ids.length; i++) {
                let pp_id = pp_ids[i];
                let i_pps = pps.id.findIndex(function(i){return i==pp_id;});
                rect[i] = {};
                rect[i].id = pps.id[i_pps];
//                rect[i].mc = pps.m_c[i];
//                rect[i].dc = pps.d_c[i];
                rect[i].info = pps.kw_bezeichnung[i_pps];
                rect[i].mc = pps.grenzkosten[i_pps]             /this.cost_units[this.cost_unit];
                rect[i].dc = pps.distance_costs[i_pps][i_dn]    /this.cost_units[this.cost_unit];
                rect[i].tc = pps.total_costs[i_pps][i_dn]       /this.cost_units[this.cost_unit];
                rect[i].p = pps.load[i_pps][i_ts]               /this.power_units[this.power_unit];
                if(i===0){
                    rect[i].p_i = 0;
                } else {
                    rect[i].p_i = rect[i-1].p_j;
                }
                rect[i].p_j = rect[i].p_i + rect[i].p
            }
            rect.colums = Object.keys(rect[0]);

            data = {'rect': rect,
                'demand': result.demand[i_ts]/this.power_units[this.power_unit],
                'price': result.price/this.cost_units[this.cost_unit]};
        }
        this.data = data
    }
}