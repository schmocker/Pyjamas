class Diagram_tP {
    constructor(parent) {

        let obj = this;
        this.run = 0;
        this.data = [];
        this.Stao_ID = "Baden"; //"";

        this.y_index = 0;

        // Margin
        this.margin = {top: 50, right: 50, bottom: 100, left: 50};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // Scale
        this.xScale = d3.scaleTime().range([0, this.width]);
        this.yScale = d3.scaleLinear().range([this.height, 0]);
        this.zScale = d3.scaleOrdinal(d3.schemeCategory10);

        // Date / Time
        this.formatTime = d3.timeFormat("%Y-%m-%d %H:%M:%S");

        // Line
        this.line = d3.line()
            .curve(d3.curveBasis)
            .x(function(d) { return obj.xScale(d.date); })
            .y(function(d) { return obj.yScale(d.value); });


        // Elements
        this.g = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g").attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        this.g.append('text').text('Tiersverlauf')
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + this.width/2 + ",-20)");

        this.xAxis = this.g.append("g")
            .attr("class", "axis axis--x")
            .attr("transform", "translate(0," + this.height + ")");

        this.yAxis = this.g.append("g")
            .attr("class", "axis axis--y");

        this.yAxis.append("text")
            .attr('class', 'title')
            .attr("transform", "rotate(-90)")
            .attr("y", -30)
            //.attr("x", -200)
            .attr("fill", "#000")
            .text("Preis [€/MWh]");

        this.legend = this.createLegend(this.g);
    }


    async updateData(){
        let obj = this;
        let query_name = 'get_mu_results';

        let filter = {'ort': ['el_rate', 'Stao_ID', 0],
            'ort2': ['el_rate', 'Stao_ID', 0]};
        filter = {};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(query_name, data_dict);

        let i_stao = -1;
        if (data) {
            i_stao = data.result.el_rate.Stao_ID.findIndex(function(i){return i==obj.Stao_ID;});
        }
        log(i_stao);

        if (data && i_stao>=0){
            this.run = data.run;
            this.data = data.result;

            // Time / Date format
            let t = this.data.times;
            let d = [];
            for (let it=0; it<t.length; it++) {
                d[it] = new Date(t[it]*1E3);
            }
            this.data.times = d;

            // Extract relevant market prices on stao_id
            let i_values = this.data.el_rate.values[i_stao];

            let data_L = i_values.map(function (c, id_c) {
                return {
                    id: id_c,
                    values: obj.data.times.map(function (d, id_d) {
                        return {
                            date: d,
                            value: i_values[id_d][id_c]
                        };
                    })
                }
            });

            this.data.data_L = data_L;

        }
    }

    async setDistNet(id){
        this.Stao_ID = id;
    }

    async updateView(updateSpeed){

        let obj = this;
        let data = this.data;


        if (data){
            /*
            let ids = data.el_rate.Stao_ID;

            let dict_er = ids.map(function(id, index) {
                return {
                    id: id,
                    borders: data.el_rate.borders[index].borders,
                    values: data.times.map(function(d, jndex) {
                        return {
                            time: data.times[jndex],
                            y: data.el_rate.values[index][jndex]
                        }
                    })
                }
            })

            // scale
            let y_min = d3.min(dict_er,
                function(a) { return d3.min(a.values,
                    function(b) {
                        return d3.min(b.y);
                    })
                });
            let y_max = d3.max(dict_er,
                function(c) { return d3.max(c.values,
                    function(d) {
                        return d3.max(d.y);
                    })
                });
            */

            let data_Ls = this.data.data_L;

            let y_min = d3.min(this.data.data_L,
                function(c) {
                    return d3.min(c.values,
                        function(d) {
                            return d.value;
                        });
            });
            let y_max = d3.max(this.data.data_L,
                function(c) {
                    return d3.max(c.values,
                        function(d) {
                            return d.value;
                        });
            });

            this.xScale.domain(d3.extent(data.times));
            this.yScale.domain([y_min, y_max]);
            this.zScale.domain(this.data.data_L.map(function(c) {return c.id;}));

            // set new data
            let data_L = this.g.selectAll(".data_L").data(data_Ls);

            // removed unused
            data_L.exit().remove();

            // add new if required
            let data_L_new = data_L.enter().append("g").attr("class", "data_L");
            data_L_new.append("path").attr("class", "line");
            data_L_new.append("text").attr("x", 3).attr("dy", "0.35em");

            // update all
            data_L = this.g.selectAll(".data_L");

            data_L.select('path')
                .transition().duration(updateSpeed)
                .attr("d", function(d) {return obj.line(d.values); })
                .style("stroke", function(d) {return obj.zScale(d.id); });

            data_L.select("text")
                .datum(function(d) {return {id: d.id, value: d.values[d.values.length - 1]}; })
                .transition().duration(updateSpeed)
                .attr("transform", function(d) { return "translate(" + obj.xScale(d.value.date) + "," + obj.yScale(d.value.value) + ")"; })
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

            this.updateLegend(updateSpeed);
            this.updateLegend(updateSpeed);


        }
    }




    // Legend
    createLegend(parent){
        let g = parent.append("g").attr('class', 'legend');
        return g;
    }
    async updateLegend(updateSpeed){
        let obj = this;
//        let items = this.data.columns.filter(function(item) { return item !== 'date' });
        let items = Object.keys(this.data.data_L);
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
            return "translate(" + 100*i + "," + 950 + ")"
        });
        legend.select('rect').style('fill', function(d) { return obj.zScale(d); });
        legend.select('text').text(function (d) { return d });
    }

}

