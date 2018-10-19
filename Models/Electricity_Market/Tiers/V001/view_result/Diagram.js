class Diagram {
    constructor(parent) {
        this.run = 0;
        this.data = [];


        this.svg = parent.append("svg").attr("id", "d3d_svg");
        this.groupeRects = this.svg.append("g");
    }

    async updateData(){
        let query_name = 'get_mu_results';

        let filter = {'ort': ['el_rate', 'Stao_ID', 0],
            'ort2': ['el_rate', 'Stao_ID', 0]};
        filter = {};
        filter = {'El_rate': ['el_rate']};
        filter = {};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(query_name, data_dict);

        if (data){
            this.run = data.run;
            this.data = data.result;
        }
    }

    updateRects(updateSpeed){
        let allRects = this.groupeRects.selectAll(".eggli").data(this.data.el_rate.Stao_ID);

        //exit
        allRects.exit().remove();

        // enter
        let allNewRects = allRects.enter().append("rect")
            .classed("eggli", true);

        // update
        this.groupeRects.selectAll(".eggli").transition().duration(updateSpeed)
            .attr("x", function(d,i){ return i*100 })
            .attr("y", function(d,i){ return i*100 })
            .attr("width", function(){ return 80 })
            .attr("height", function(){ return 80 });
    }
}
