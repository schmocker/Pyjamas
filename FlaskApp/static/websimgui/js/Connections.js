class Connections {
    constructor() {
        let obj = this;
        this.menu = [{
            title: "Remove",
            action: async function(elm, d, i) {await obj.remove(d.id)}
        }];
    }
    async build(){
        let connections = main.selectAll(".connection").data(agent_data.connection);

        //exit
        connections.exit().remove();

        //enter
        connections = connections.enter().append("g")
            .classed("connection",true)
            .attr("id", function (d) { return d.id; });


        connections.append("line")
            .classed("line",true)
            .on("mouseover", function(d){d3.select(this).classed("line_hover",true);})
            .on("mouseout", function(d){d3.select(this).classed("line_hover",false);})
            .on("contextmenu", contextMenu.onContextMenu(this.menu));

        await this.update();
    }

    async update(){
        let connections = main.selectAll(".connection");
        connections.select(".line")
            .attr("x1", function (d) {return d3.selectAll("#" + d.port_id_from).data()[0].linepoint[0]})
            .attr("y1", function (d) {return d3.selectAll("#" + d.port_id_from).data()[0].linepoint[1]})
            .attr("x2", function (d) {return d3.selectAll("#" + d.port_id_to).data()[0].linepoint[0]})
            .attr("y2", function (d) {return d3.selectAll("#" + d.port_id_to).data()[0].linepoint[1]});
    }

    async add(arrow1, arrow2){
        await post("add_connection",
            {
                'fk_model_used_from': arrow1.data()[0].model,
                'port_id_from': arrow1.attr("id"),
                'fk_model_used_to': arrow2.data()[0].model,
                'port_id_to': arrow2.attr("id")
            },true);
    }

    async remove(id){
        await post("remove_connection",{'connection': id},true);
    }
}
