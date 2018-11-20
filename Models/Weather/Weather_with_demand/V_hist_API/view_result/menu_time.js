class MenuTime {
    constructor(parent) {
        let obj = this;
        this.run = 0;


        this.time_menu = parent.append("div").classed('time_menu', true);
        this.time_svg = this.time_menu.append("svg").classed('time_svg', true)
            .attr("width", window.innerWidth);

        let radius = 9;
        let margin_hor = radius;  // this.time_svg.node().getBoundingClientRect().width/20;
        let margin_factor = 3;
        let vertical_offset = 0.5;
        this.margin = {left: margin_hor, right: margin_hor};
        this.width = this.time_svg.node().getBoundingClientRect().width - margin_factor*this.margin.left - 6*margin_factor*this.margin.right;
        this.height = this.time_svg.node().getBoundingClientRect().height*(1+vertical_offset);
        this.x = d3.scaleLinear().range([0, this.width]).clamp(true);

        this.slider = this.time_svg.append("g")
            .attr("class", "slider")
            .attr("transform", "translate(" + margin_factor*this.margin.left + "," + this.height / 2 + ")");

        this.slider.append("line")
            .attr("class", "track")
            .attr("x1", obj.x.range()[0])
            .attr("x2", obj.x.range()[1])
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-inset")
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-overlay");

        this.ticks = this.slider.insert("g", ".track-overlay")
            .attr("class", "ticks")
            .attr("transform", "translate(0," + 18 + ")");

        this.handle = this.slider.insert("circle", ".track-overlay")
            .attr("class", "handle")
            .attr("r", radius);

        this.dates = this.slider.append("g")
            .attr("class", "dates");

        this.start();
    }

    async start(){
        await this.updateData();
        if (this.futures){
            await d_map.setTimeType(0);
        }
    }

    async updateData() {

        let filter = {'futures': ['Map_weather','futures']};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(data_dict);
        data = JSON.parse(data);

        //let data = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': this.run, 'filter': this.filter});
        if (data) {

            let obj = this;
            this.run = data.run;
            this.futures = data.result.futures;

        }
    }

    updateMenuTime(updateSpeed){

        let obj = this;

        let i_times = [0, this.futures.length - 1];
        this.x.domain(i_times);

        let allTicks = this.ticks.selectAll(".cn")
            .data(this.x.ticks(i_times[1]));


        allTicks.enter().append("text")
            .attr("class", "cn")
            .attr("x", this.x)
            .attr("y", 5)
            .attr("text-anchor", "middle")
            .text(function (d) { return d });

        let slider = this.slider.selectAll("line")
            .call(d3.drag()
                .on("drag", async function() {
                    let h = obj.x.invert(d3.event.x);
                    let i_ts = Math.round(h);
                    d_map.setTimeType(i_ts);
                    obj.handle.attr("cx", obj.x(i_ts));
                })/*
                .on("end", async function() {
                    let h = obj.x.invert(d3.event.x);
                    let i_ts = Math.round(h);
                    console.log(i_ts);
                    await updateAll(500);
                })*/);

        let allDates = this.dates.selectAll("text")
            .data(this.futures);
        allDates.exit().remove();

        let allDates_x = 0;
        let allDates_y = -10;
        let allDates_dx = this.width/(this.futures.length-1);
        allDates.enter().append("text")
            .attr("text-anchor", "start") //"middle")
            .attr("x", allDates_x)
            .attr("y", allDates_y);

        allDates = this.dates.selectAll("text");
        allDates
            .attr("transform", function(d, i) {
                return "translate(" + allDates_x + allDates_dx*i + "," + allDates_y + ")rotate(-30)"
            })
            .text(function (d) {
                return new Date(d*1E3).timeformat()
            });

    }
}


Date.prototype.timeformat = function() {
    return date = this.getFullYear() + "-" +
        ((this.getMonth()+1)<10?'0':'') + (this.getMonth()+1) + "-" +
        (this.getDate()<10?'0':'') + this.getDate() + " " +
        (this.getHours()<10?'0':'') + this.getHours() + ":" +
        (this.getMinutes()<10?'0':'') + this.getMinutes() + ":" +
        (this.getSeconds()<10?'0':'') + this.getSeconds();
};