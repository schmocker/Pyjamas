class Menu {
    constructor(parent) {
        this.run = 0;
        this.data = null;
        this.parent = parent;

        this.start();
    }

    async start(){
        await this.updateData();
        if(this.pp_types){
            await d_map.setPPtype(this.pp_types[0]); // ?????????????????
        }
    }

    updateMenu(updateSpeed){
        let obj = this;
        let allButtons = this.parent.selectAll(".cn").data(this.pp_types);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d })
            .classed("cn", true)
            .on('click', function(d) {
                obj.parent.selectAll(".cn").classed("cn_active", false);
                d3.select(this).classed("cn_active", true);
                d_map.setPPtype(d);
                //console.log(d);
            })
            .each(function (d,i) {
                if(i===0){
                    d3.select(this).classed("cn_active", true);
                }
            });
    }

    async updateData(){
        let filter = {};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(data_dict);
        data = JSON.parse(data);

        if (data){
            this.run = data.run;
            let type_temp = data.result.kw_park["bez_kraftwerkstyp"];
            let types = type_temp.unique();
            this.pp_types = types;
        }
    }
}

Array.prototype.unique = function() {
  return this.filter(function (value, index, self) {
    return self.indexOf(value) === index;
  });
};