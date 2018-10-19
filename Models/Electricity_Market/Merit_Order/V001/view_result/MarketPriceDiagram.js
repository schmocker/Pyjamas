class MarketPriceDiagram {
    constructor(parent) {
        let obj = this;
        this.run = 0;

        this.cost_units = {'E_J': 1E0,'E_kWh': 1/3.6E6,'E_MWh': 1/3.6E9};
        this.cost_unit = 'E_MWh';

        this.data = null;

        this.filter = {'t': ['all_data', 'times'], 'p': ['market_prices']};

        this.div = parent.append("div").attr("class", "tooltip");

        this.margin = {top: 50, right: 50, bottom: 100, left: 50};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        this.xScale = d3.scaleTime().range([0, this.width]);
        this.yScale = d3.scaleLinear().range([this.height, 0]);
        this.zScale = d3.scaleOrdinal(d3.schemeCategory10);

        this.formatTime = d3.timeFormat("%Y-%m-%d %H:%M:%S");

        this.line = d3.line()
            .x(function(d) { return obj.xScale(d.date); })
            .y(function(d) { return obj.yScale(d.y); });


        // append elements
        this.g = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g").attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        this.g.append('text').text('Marktpreisverlauf für die einzelnen Verteilnetze')
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + this.width/2 + ",-20)");

        this.timeLine = this.createTimeLine(this.g);

        this.xAxis = this.g.append("g")
            .attr("class", "axis axis--x")
            .attr("transform", "translate(0," + this.height + ")");

        this.yAxis = this.g.append("g")
            .attr("class", "axis axis--y");

        this.yAxis.append("text")
            .attr('class', 'title')
            .attr("transform", "rotate(-90)")
            .attr("y", -30)
            .attr("fill", "#000")
            .text("Marktpreis [€/MWh]");

        this.legend = this.createLegend(this.g);
    }

    async updateView(updateSpeed){

        let obj = this;
        let data = this.data;

        if (data){
            let ids = data.columns.filter(function(item) { return item !== 'date' });
            let dist_nets = ids.map(function(id) {
                return {
                    id: id,
                    values: data.map(function(d) {
                        return {date: d.date, y: d[id]};
                    })
                };
            });

            this.xScale.domain(d3.extent(data, function(d) { return d.date; }));
            this.yScale.domain([
                0, //d3.min(dist_nets, function(c) { return d3.min(c.values, function(d) { return d.y; }); }),
                50//d3.max(dist_nets, function(c) { return d3.max(c.values, function(d) { return d.y; }); })
            ]);
            this.zScale.domain(dist_nets.map(function(c) { return c.id; }));

            // set new data
            let dist_net = this.g.selectAll(".dist_net").data(dist_nets);

            // remove unused
            dist_net.exit().remove();

            // add new if required
            let new_dist_net = dist_net.enter().append("g").attr("class", "dist_net");
            new_dist_net.append("path").attr("class", "line");
            new_dist_net.append("text").attr("x", 3).attr("dy", "0.35em");

            // update all
            dist_net = this.g.selectAll(".dist_net");

            dist_net.select('path')
                .transition().duration(updateSpeed)
                .attr("d", function(d) { return obj.line(d.values); })
                .style("stroke", function(d) { return obj.zScale(d.id); });

            dist_net.select("text")
                .datum(function(d) { return {id: d.id, value: d.values[d.values.length - 1]}; })
                .transition().duration(updateSpeed)
                .attr("transform", function(d) { return "translate(" + obj.xScale(d.value.date) + "," + obj.yScale(d.value.y) + ")"; })
                .text(function(d) { return d.id; });


            // update axis
            this.xAxis
                .transition().duration(updateSpeed)
                .call(d3.axisBottom(this.xScale).tickFormat(this.formatTime))
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "0em").attr("dy", "1em")
                .attr("transform", "rotate(-15)");

            this.yAxis
                .transition().duration(updateSpeed)
                .call(d3.axisLeft(this.yScale));

            this.updateTimeLine(updateSpeed);
            this.updateLegend(updateSpeed);



            ////////////////////////////////
/*

            let legend5 = d3.select('.legend').selectAll("legend").data(['a','b']);

            legend5.enter().append("div")
                .attr("class","legends5");

            let p = legend5.append("p").attr("class","country-name");
            p.append("span").attr("class","key-dot").style("background",function(d,i) { return color(i) } );
            p.insert("text").text(function(d,i) { return d } )
*/
        }
    }

    // Legend
    createLegend(parent){
        let g = parent.append("g").attr('class', 'legend');
        return g;
    }
    async updateLegend(updateSpeed){
        let obj = this;
        let items = this.data.columns.filter(function(item) { return item !== 'date' });
        let legend = this.legend.selectAll('.legend_item').data(items);

        // exit
        legend.exit().remove();

        // enter
        let new_legend = legend.enter().append('g').attr('class', 'legend_item');

        let size = 10;
        new_legend.append('rect').attr('x', 0).attr('y', -size/2).attr('width', size).attr('height', size);
        new_legend.append('text').style('alignment-baseline','central').attr('x', size+5);

        // update
        legend = this.legend.selectAll('.legend_item');
        legend.attr("transform", function (d, i) {
            return "translate(" + 100*i + "," + 330 + ")"
        });
        legend.select('rect').style('fill', function(d) { return obj.zScale(d); });
        legend.select('text').text(function (d) { return d });
    }





    createTimeLine(parent){
        let g = parent.append("g");
        g.append("line");
        g.append("text").style("font-size", "10px").attr('x', 5).attr('y', -5);
        return g;
    }

    async updateTimeLine(updateSpeed){
        let obj = this;
        this.timeLine.select('line')
            .transition().duration(updateSpeed)
            .attr("x1", function () { return obj.xScale(obj.data[i_ts].date)})
            .attr("x2", function () { return obj.xScale(obj.data[i_ts].date)})
            .attr("y1", function () { return obj.yScale(0)})
            .attr("y2", function () { return obj.yScale(obj.yScale.domain()[1])});

        this.timeLine.select('text')
            .text(function () { return obj.formatTime(obj.data[i_ts].date) })
            .attr("transform", function() { return "translate(" + obj.xScale(obj.data[i_ts].date) + "," + obj.yScale(0) + ")"; })
    }


    async updateData(){
        let data = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': this.run, 'filter': this.filter});
        if (data){
            this.run = data.run;
            let result = data.result;

            let t = result.t;
            let dn_ids = result.p.distribution_networks;
            let p = result.p.prices;



            let d = [];
            for(let i_t = 0; i_t < t.length; i_t++) {
                d[i_t] = {};
                d[i_t].date = new Date(t[i_t]*1E3);
                for(let i_dn = 0; i_dn < dn_ids.length; i_dn++) {
                    d[i_t][dn_ids[i_dn]] = p[i_dn][i_t]/this.cost_units[this.cost_unit];
                }
            }
            d.columns = Object.keys(d[0]);

            data = d;

        }
        this.data = data
    }
}