class Menu {
    constructor(parent) {
        this.run = 0;
        this.data = null;
        this.parent = parent;

        this.start();
    }

    async start(){
        await this.updateData();
        if(this.meteo_types){
            await d_map.setMeteoType(this.meteo_types[0]);
        }
    }

    updateMenu(updateSpeed){
        let obj = this;
        let allButtons = this.parent.selectAll(".cn").data(this.meteo_types);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d })
            .classed("cn", true)
            .on('click', function(d) {
                obj.parent.selectAll(".cn").classed("cn_active", false);
                d3.select(this).classed("cn_active", true);
                d_map.setMeteoType(d);
                //console.log(d);
            })
            .each(function (d,i) {
                if(i===0){
                    d3.select(this).classed("cn_active", true);
                }
            });
    }

    async updateData(){
        this.meteo_types = ["Temperature", "Wind speed", "Radiation"];
    }
}

Array.prototype.unique = function() {
  return this.filter(function (value, index, self) {
    return self.indexOf(value) === index;
  });
};