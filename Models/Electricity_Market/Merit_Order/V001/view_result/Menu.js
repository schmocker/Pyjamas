class Menu {
    constructor(parent) {
        let obj = this;
        this.run = 0;


        this.time_menu = parent.append("div").classed('time_menu', true);
        this.time_title = this.time_menu.append("div").classed('time_title', true).html('<h2>Time: </h2>');
        this.time_label = this.time_menu.append("div").classed('time_label', true);
        this.time_svg = this.time_menu.append("svg").classed('time_svg', true);

        this.dn_menu = parent.append("div").classed('dn_menu', true);
        this.dn_title = this.dn_menu.append("div").classed('dn_title', true).html('<h2>Distribution Network: </h2>');
        this.dn_select = this.dn_menu.append("select")
            .classed('dn_select', true)
            .on('change',async function () {
                let selectValue = d3.select(this).property('value');
                i_dn = obj.dns.indexOf(selectValue);
                mo_diag.run = 0;
                await updateAll(500);
            });

        this.dns = null;



        this.filter = {'t': ['fut2'], 'dn': ['sorted_pp_id', 'distribution_networks']};

        let radius = 9;
        let margin_hor = radius;  // this.time_svg.node().getBoundingClientRect().width/20;
        this.margin = {left: margin_hor, right: margin_hor};
        this.width = this.time_svg.node().getBoundingClientRect().width - this.margin.left - this.margin.right;
        this.height = this.time_svg.node().getBoundingClientRect().height;
        this.x = d3.scaleLinear().range([0, this.width]).clamp(true);

        this.times = null;




        this.slider = this.time_svg.append("g")
            .attr("class", "slider")
            .attr("transform", "translate(" + this.margin.left + "," + this.height / 2 + ")");

        this.slider.append("line")
            .attr("class", "track")
            .attr("x1", obj.x.range()[0])
            .attr("x2", obj.x.range()[1])
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-inset")
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-overlay")
            .call(d3.drag()
                .on("start drag", async function() {
                    let h = obj.x.invert(d3.event.x);
                    i_ts = Math.round(h);
                    handle.attr("cx", obj.x(i_ts));
                    let t = obj.times[i_ts]*1000;
                    obj.time_label.html(new Date(t));
                    await mp_diag.updateTimeLine(0);
                })
                .on("end", async function() {
                    let h = obj.x.invert(d3.event.x);
                    i_ts = Math.round(h);
                    console.log(i_ts);
                    mo_diag.run = 0;
                    await updateAll(500);
                }));

        this.ticks = this.slider.insert("g", ".track-overlay")
            .attr("class", "ticks")
            .attr("transform", "translate(0," + 18 + ")");



        let handle = this.slider.insert("circle", ".track-overlay")
            .attr("class", "handle")
            .attr("r", radius);



    }

    async update() {
        let data = await get('get_mu_results', {'mu_id': mu_id, 'mu_run': this.run, 'filter': this.filter});
        if (data) {

            this.run = data.run;
            this.dns = data.result.dn;

            this.dn_select.selectAll('option').remove();
            this.dn_select.selectAll('option').data(this.dns).enter()
                .append('option')
                .attr('value', function (d) {
                    return d
                })
                .html(function (d) {
                    return d
                });

            this.times = data.result.t;

            let i_times = [0, this.times.length - 1];

            this.x.domain(i_times);

            this.ticks.selectAll("text")
                .data(this.x.ticks(i_times[1] / 6))
                .enter().append("text")
                .attr("x", this.x)
                .attr("text-anchor", "middle")
                .text(function (d) {
                    return d;
                });
        }
    }
}