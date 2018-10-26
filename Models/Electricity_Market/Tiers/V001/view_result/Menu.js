class Menu {
    constructor(parent) {
        this.run = 0;
        this.data = [];
        this.parent = parent;
    }

    updateMenu(updateSpeed){
        let allButtons = this.parent.selectAll(".cn").data(this.data);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d })
            .classed("cn", true)
            .on('click', function(d) {
                diag.setDistNet(d);
                log(d);
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
