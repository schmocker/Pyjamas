// export
class Connections {
    constructor(parent) {
        this.parent = parent;
        let obj = this;
        this.menu = [{
            title: "Remove",
            action: async function(elm, d, i) {await obj.remove(d.key)}
        }];
    }
    async build(){
        let connections = this.parent.main.selectAll(".connection").data(d3.entries(this.parent.data.connection));

        //exit
        connections.exit().remove();

        //enter
        connections = connections.enter().append("g")
            .classed("connection",true)
            .attr("id", function (d) { return d.key; });


        connections.append("line")
            .classed("line",true)
            .on("mouseover", function(d){d3.select(this).classed("line_hover",true);})
            .on("mouseout", function(d){d3.select(this).classed("line_hover",false);})
            .on("contextmenu", this.parent.contextMenu.onContextMenu(this.menu));

        await this.update();
    }

    async update(){
        let obj = this;
        let connections = this.parent.main.selectAll(".connection");
        connections.select(".line")
            .attr("x1", function (d) {return obj.get_point(d,'from','x') })
            .attr("y1", function (d) {return obj.get_point(d,'from','y') })
            .attr("x2", function (d) {return obj.get_point(d,'to','x') })
            .attr("y2", function (d) {return obj.get_point(d,'to','y') });
    }

    get_point(d, from_to, x_y){
        let model_id =  '#mu_'+d.value['fk_model_used_'+from_to];
        let port_id = " #" + d.value['port_id_'+from_to];
        x_y = (x_y === 'y') ? 1 : 0;
        return d3.select(model_id+" "+port_id).data()[0].linepoint[x_y];
    }

    async add(arrow1, arrow2){
        await this.parent.post("add_connection",
            {
                'fk_mu_from': arrow1.data()[0].model,
                'port_id_from': arrow1.attr("id"),
                'fk_mu_to': arrow2.data()[0].model,
                'port_id_to': arrow2.attr("id")
            },true);
    }

    async remove(id){
        await this.parent.post("remove_connection",{'connection': id},true);
    }
}
