class Menu {
    constructor(parent) {
        this.run = 0;
        this.data = null;
        this.parent = parent;

        this.start();
    }

    async start(){
        await this.updateData();
        if(this.data){
            await diag.setDistNet(this.data[0]);
            await diag_tiers_try.setDistNet(this.data[0]);
            await diag_int_try.setDistNet(this.data[0]);
        }
    }

    updateMenu(updateSpeed){
        let obj = this;
        let allButtons = this.parent.selectAll(".cn").data(this.data);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d })
            .classed("cn", true)
            .on('click', function(d) {
                obj.parent.selectAll(".cn").classed("cn_active", false);
                d3.select(this).classed("cn_active", true);
                diag.setDistNet(d);
            })
            .each(function (d,i) {
                if(i===0){
                    d3.select(this).classed("cn_active", true);
                }
            });
    }

    async updateData(){
        let filter = {'orte': ['el_rate', 'Stao_ID']};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(data_dict);
        data = JSON.parse(data);

        if (data){
            this.run = data.run;
            this.data = data.result.orte;
        }
    }
}
