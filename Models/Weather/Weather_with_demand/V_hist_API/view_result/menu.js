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
        let allButtons = this.parent.selectAll(".cn").data(this.meteo_types);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d })
            .classed("cn", true)
            .on('click', function(d) {
                d_map.setMeteoType(d);
                //console.log(d);
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