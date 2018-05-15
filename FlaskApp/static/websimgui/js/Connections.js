class Connections {
    constructor() {
        let obj = this;
        this.menu = [{
            title: "Remove",
            action: async function(elm, d, i) {await obj.remove(elm, d, i)}
        }];
    }
    async update(){
        let connections = main.selectAll(".connection").data(agent_data.connections);

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
            .on("contextmenu", await onContextMenu(this.menu));
    }

    async update_position(){
        let connections = main.selectAll(".connection");
        connections.select(".line")
            .attr("x1", function (d) {return d3.select("#" + d.port_id_from + "[id_model='"+d.fk_model_used_from+"']").data()[0].arrow.line_point_x})
            .attr("y1", function (d) {return d3.select("#" + d.port_id_from + "[id_model='"+d.fk_model_used_from+"']").data()[0].arrow.line_point_y})
            .attr("x2", function (d) {return d3.select("#" + d.port_id_to + "[id_model='"+d.fk_model_used_to+"']").data()[0].arrow.line_point_x})
            .attr("y2", function (d) {return d3.select("#" + d.port_id_to + "[id_model='"+d.fk_model_used_to+"']").data()[0].arrow.line_point_y});
    }

    async add(arrow1, arrow2){
        let data = await $.post("/websimgui", {
                'fnc': 'add_connection',
                'data': JSON.stringify({
                    'agent': agent_data.id,
                    'fk_model_used_from': arrow1.data()[0].model.id,
                    'port_id_from': arrow1.data()[0].id,
                    'fk_model_used_to': arrow2.data()[0].model.id,
                    'port_id_to': arrow2.data()[0].id})});
        data = await decode_data(JSON.parse(data));
        await update_all_2(data)
    }

    async remove(elm, d, i){
        let data = await $.post("/websimgui", {
                'fnc': 'remove_connection',
                'data': JSON.stringify({
                    'agent': agent_data.id,
                    'connection': d.id
                })
            });
        data = await decode_data(JSON.parse(data));
        await update_all_2(data)
    }
}
