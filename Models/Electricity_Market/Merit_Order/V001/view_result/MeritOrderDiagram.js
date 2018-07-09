class MeritOrderDiagram {
    constructor(parent) {
        this.run = 0;

        this.power_units = {'W': 1E0,'kW': 1E3,'MW': 1E6,'GW': 1E9,'TW': 1E12};
        this.power_unit = 'TW';

        this.data = null;

        this.div = parent.append("div").attr("class", "tooltip");

        this.margin = {top: 20, right: 50, bottom: 50, left: 50};
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

        this.yLabel = this.createXLabel(this.svg);

    }

    async updateView(updateSpeed){
        let obj = this;
        let data = this.data;

        if (data){

            // Scale the range of the data
            this.xScale.domain([0, d3.max(data.rect, function(d) { return d.p_j; })*1.05]);
            this.yScale.domain([0, (data.rect[data.rect.length-1].mc + data.rect[data.rect.length-1].dc)*1.05]);
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
                .attr("x1", function () { return obj.xScale(data.d)})
                .attr("x2", function () { return obj.xScale(data.d)})
                .attr("y1", function () { return obj.yScale(0)})
                .attr("y2", function () { return obj.yScale(data.price)});
            this.priceLine
                .transition().duration(updateSpeed)
                .attr("x1", function () { return obj.xScale(data.d)})
                .attr("x2", function () { return obj.xScale(0)})
                .attr("y1", function () { return obj.yScale(data.price)})
                .attr("y2", function () { return obj.yScale(data.price)});

            this.priceText
                .transition().duration(updateSpeed)
                .text(function () { return "Market price: " + data.price.toFixed(2) + " CHF/MWh" })
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
        this.yLabel
            .transition().duration(updateSpeed)
            .text('Power ['+this.power_unit+']')
            .attr("transform", function() { return "translate(" + obj.xScale(obj.xScale.domain()[1]/2) + "," + obj.yScale(0-obj.yScale.domain()[1]/9) + ")"; });
    }



    async updateData(){
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
                rect[i].p = pps.p[i]/this.power_units[this.power_unit];
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
                'd': result.d/this.power_units[this.power_unit],
                'price': result.price};
        }
        this.data = data
    }

}