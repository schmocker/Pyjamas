class MarketPriceDiagram {
    constructor(parent) {
        this.run = 0;

        this.filter = {'t': ['all_data', 'times'], 'p': ['market_prices']};

        this.div = parent.append("div").attr("class", "tooltip");

        this.margin = {top: 20, right: 50, bottom: 50, left: 50};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // set the ranges
        this.x = d3.scaleTime().range([0, this.width]);
        this.y = d3.scaleLinear().range([this.height, 0]);
        this.z = d3.scaleOrdinal(d3.schemeCategory10);

        this.line = d3.line()
            .curve(d3.curveBasis)
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.y); });

        // append the svg obgect to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g").attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        this.formatTime = d3.timeFormat("%Y-%m-%d %H:%M:%S");
    }

    async update(){
        let obj = this;
        let data = await this.get_data();

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

            this.x.domain(d3.extent(data, function(d) { return d.date; }));

            this.y.domain([
                d3.min(dist_nets, function(c) { return d3.min(c.values, function(d) { return d.y; }); }),
                d3.max(dist_nets, function(c) { return d3.max(c.values, function(d) { return d.y; }); })
            ]);

            this.z.domain(dist_nets.map(function(c) { return c.id; }));

            this.svg.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", "translate(0," + this.height + ")")
                .call(d3.axisBottom(this.x));

            this.svg.append("g")
                .attr("class", "axis axis--y")
                .call(d3.axisLeft(this.y))
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", "0.71em")
                .attr("fill", "#000")
                .text("Temperature, ºF");

            let dist_net = g.selectAll(".dist_net")
                .data(dist_nets)
                .enter().append("g")
                .attr("class", "dist_net");

            dist_net.append("path")
                .attr("class", "line")
                .attr("d", function(d) { return this.line(d.values); })
                .style("stroke", function(d) { return this.z(d.id); });

            dist_net.append("text")
                .datum(function(d) { return {id: d.id, value: d.values[d.values.length - 1]}; })
                .attr("transform", function(d) { return "translate(" + this.x(d.value.date) + "," + this.y(d.value.y) + ")"; })
                .attr("x", 3)
                .attr("dy", "0.35em")
                .style("font", "10px sans-serif")
                .text(function(d) { return d.id; });


        }
    }


    async get_data(){
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
                    d[i_t][dn_ids[i_dn]] = p[i_dn][i_t];
                }
            }
            d.columns = Object.keys(d[0]);

            data = d;
        }
        return data
    }
}