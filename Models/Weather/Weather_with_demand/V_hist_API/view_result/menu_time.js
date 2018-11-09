class MenuTime {
    constructor(parent) {
        this.run = 0;
        this.data = null;
        this.parent = parent;

        this.start();
    }

    async start(){
        await this.updateData();
        if(this.time_types){
            await d_map.setTimeType(this.time_types[0]);
        }
    }

    updateMenuTime(updateSpeed){
        let allButtons = this.parent.selectAll(".cn").data(this.time_types);

        allButtons.exit().remove();

        allButtons.enter().append("button")
            .text(function (d) { return d })
            .classed("cn", true)
            .on('click', function(d) {
                d_map.setTimeType(d);
                //console.log(d);
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