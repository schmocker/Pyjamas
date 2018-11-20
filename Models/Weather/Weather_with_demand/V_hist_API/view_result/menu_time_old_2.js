class MenuTime_2 {
    constructor(parent) {
        this.run = 0;
        this.data = null;
        this.parent = parent;
        let obj = this;

        this.start();

        // Margin
        this.margin = {top: 50, right: 75, bottom: 50, left: 50};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = 50;
        this.radius = 9;

        this.time_title = this.parent.append("div")
            .attr("class", "time_title")
            .html('<h2>Time: </h2>');
        this.time_label = this.parent.append("div")
            .attr("class", "time_label");
        this.time_svg = this.parent.append("svg")
            .attr("class", "time_svg");

        this.x = d3.scaleLinear()
            .domain([0, 180])
            .range([0, this.width])
            .clamp(true);

        // slider
        this.slider = this.time_svg.append("g")
            .attr("class", "slider")
            .attr("transform", "translate(" + this.margin.left + "," + this.height / 2 + ")");

        this.lines = this.slider.append("line")
            .attr("class", "track")
            .attr("x1", obj.x.range()[0])
            .attr("x2", obj.x.range()[1])
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-inset")
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-overlay")
            .call(d3.drag()
                .on("start.interrupt", function() { slider.interrupt(); })
                .on("start drag", function() { hue(x.invert(d3.event.x)); }));
        /*
                .on("start drag", async function() {
                    let h = obj.x.invert(d3.event.x);
                    i_ts = Math.round(h);
                    obj.handle.attr("cx", obj.x(i_ts));
                    let t = obj.times[i_ts]*1000;
                    obj.time_label.html(new Date(t));
                    //await mp_diag.updateTimeLine(0);
                })
                .on("end", async function() {
                    let h = obj.x.invert(d3.event.x);
                    i_ts = Math.round(h);
                    console.log(i_ts);
                    //mo_diag.run = 0;
                    await updateAll(500);
                }));*/

        this.ticks = this.slider.insert("g", ".track-overlay")
            .attr("class", "ticks")
            .attr("transform", "translate(0," + 18 + ")");

        this.handle = this.slider.insert("circle", ".track-overlay")
            .attr("class", "handle")
            .attr("r", this.radius);
    }

    async start(){
        await this.updateData();
        if(this.time_types){
            await d_map.setTimeType(this.time_types[0]);
        }
    }

    updateMenuTime(updateSpeed){

        let i_times = [0, this.time_types.length - 1];
        this.x.domain(i_times);
/*
        this.slider_line = this.slider.selectAll("line")
            .call(d3.drag()
                .on("start drag", async function() {
                    let h = obj.x.invert(d3.event.x);
                    i_ts = Math.round(h);
                    obj.handle.attr("cx", obj.x(i_ts));
                    let t = obj.times[i_ts]*1000;
                    obj.time_label.html(new Date(t));
                    //await mp_diag.updateTimeLine(0);
                })
                .on("end", async function() {
                    let h = obj.x.invert(d3.event.x);
                    i_ts = Math.round(h);
                    console.log(i_ts);
                    //mo_diag.run = 0;
                    await updateAll(500);
                }));
*/
        this.ticks.selectAll("text")
            .data(this.x.ticks(i_times[1]))
            .enter().append("text")
            .attr("x", this.x)
            .attr("text-anchor", "middle")
            .text(function (d) {
                return d;
            });
    }

    async updateData(){
        let filter = {'futures': ['Map_weather','futures']};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(data_dict);
        data = JSON.parse(data);

        if (data){
            this.run = data.run;
            let futures = data.result.futures;
            this.futures = futures;
            futures = futures.map(function (c) {return new Date(c*1E3)});
            futures = futures.map(function (d) {return d.timeformat()});
            this.time_types = futures;
        }
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