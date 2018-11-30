class Buttons {
    constructor(parent) {
        this.run = 0;
        this.data = null;
        this.parent = parent;

        this.parent.attr("class", "tab");

        //this.diag_tiers = new Diagram(this.tiers);
        //this.diag_timeseries = new Diagram(this.timeseries);
        //this.diag_integrated = new Diagram(this.integrated);

        // Start
        this.start();

    }

    async start(){
        await this.updateData();
        if(this.diag_types){
            //await diag.setDiagTyp(this.diag_types[0]);
            d3.selectAll('.tabcontent').style("display", "none");
            d3.select('#' + this.diag_types[0].key + '.tabcontent').style("display", "block");
            d3.selectAll('.tablinks').classed("tab_active", false);

        }
    }

    updateMenu(updateSpeed){
        let obj = this;
        let allButtons = this.parent.selectAll(".tablinks").data(this.diag_types);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d.value })
            .attr("class", "tablinks")
            .attr("id", function (d, id_d) { return id_d })
            .on('click', function(d, id_d) {
                d3.selectAll('.tabcontent').style("display", "none");
                d3.select('#' + d.key + '.tabcontent').style("display", "block");
                d3.selectAll('.tablinks').classed("tab_active", false);
                //d3.select('#' + id_d + ' .tablinks').classed("tab_active", true);
                d3.select(this).classed("tab_active", true);
            })
            .each(function (d,i) {
                if(i===0){
                    d3.select(this).classed("tab_active", true);
                }
            });
    }

    async updateData(){
        this.diag_types = {d3_tiers: "ET & NT Tiers", d3_timeseries: "Time series", d3_integrated: "Costs"};

        this.diag_types = d3.entries(this.diag_types);
    }
}
