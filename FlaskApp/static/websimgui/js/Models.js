class Models {
    constructor() {
        let obj = this;
        this.menu = [
            {title: "Informationen",
            action: async function(elm, d, i) {alert("Model infos not yet available");}}, // Todo: Modelinfos anzeigen
            {title: "Remove",
            action: async function(elm, d, i) {await obj.remove(elm, d, i)}}];
    }

    async update(){
        main.selectAll(".model").remove();//// !!!!!!!!!!!!!!!!!!!
        let objs = main.selectAll(".model").data(agent_data.models);

        //exit
        objs.exit().remove();
        //models.remove();
        //models = main.selectAll(".model").data(agent_data.models);

        //enter
        objs = objs.enter().append("g")
            .classed("model",true)
            .attr("id", function (d) { return d.id_html; });
        objs.append("rect")
            .classed("box",true)
            .call(await this.onModelDrag())
            .on("contextmenu", await onContextMenu(this.menu));
        objs.append("text")
            .classed("model_name",true)
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "top")
            .call(await this.onModelDrag());

        objs.append("rect")
            .classed("sizer",true)
            .call(await this.onModelResize());

        let directions = ['inputs', 'outputs'];
        for (let i = 0; i < directions.length; i++) {
            let direction = directions[i];




            let rail = objs.append("g")
                .classed(direction, true);


            let ports = rail.selectAll(".port").data(function (d) {return d[direction].ports });
            ports.exit().remove();
            ports = ports.enter().append("g")
                .classed("port", true)
                .attr("id", function (d) {
                    return d.id;
                })
                .attr("id_model", function (d) {
                    return d.id_model
                });
            ports.append("polyline")
                .classed("arrow", true)
                .call(await this.onConnecting());
            ports.append("text")
                .classed("port_name", true);
        }
    }

    async update_position(){
        let models = main.selectAll(".model");

        models.select(".box")
            .attr("x", function(d) { return d.x; })
            .attr("y", function(d) { return d.y; })
            .attr("width", function(d) { return d.width; })
            .attr("height", function(d) { return d.height; });

        models.select(".model_name")
            .attr("x", function(d) { return d.name_pos.x; })
            .attr("y", function(d) { return d.name_pos.y; })
            .text(function(d) { return d.name; });

        models.select(".sizer")
            .attr("x", function (d) { return d.sizer.x })
            .attr("y", function (d) { return d.sizer.y })
            .attr("width", function (d) { return d.sizer.size })
            .attr("height", function (d) { return d.sizer.size });

        let ports = main.selectAll(".port");
        ports.select(".port_name")
            .attr("x", function(d){ return d.text.x; })
            .attr("y", function(d){ return d.text.y; })
            .text(function(d) { return d.name; })
            .attr("text-anchor", function(d) { return d.text.anchor})
            .attr("alignment-baseline", function(d) { return d.text.baseline});

        ports.select(".arrow")
            .attr("points", function(d){ return d.arrow.points; });
    }

    async add(name, fk_model){
        let data = await $.post("/websimgui", {
                'fnc': 'add_model_used',
                'data': JSON.stringify({
                    'agent': agent_data.id,
                    'name': name,
                    'fk_model': fk_model})});
        data = await decode_data(JSON.parse(data));
        await update_all_2(data);
    }

    async remove(elm, d, i){
        let data = await $.post("/websimgui", {
                'fnc': 'remove_model',
                'data': JSON.stringify({
                    'agent': agent_data.id,
                    'model': d.id
                })
            });
        data = await decode_data(JSON.parse(data));
        await update_all_2(data);
    }

    async onModelDrag() {
        return d3.drag()
            .on("start", async function (d) {})
            .on("drag", async function (d) {
                d.x = d.x + d3.event.dx;
                d.y = d.y + d3.event.dy;
                await update_positions();
            })
            .on("end", async function (d) {
                let data = await $.post("/websimgui", {
                    'fnc': 'set_model_pos',
                    'data': JSON.stringify({
                        'agent': agent_data.id,
                        'model': d.id,
                        'x': d.x,
                        'y': d.y})});
                data = await decode_data(JSON.parse(data));
                await update_all_2(data);
            })
    }

    async onModelResize() {
        return d3.drag()
            .on("start", async function (d) {})
            .on("drag", async function (d) {
                d.width = Math.max(d.width+d3.event.dx,30);
                d.height = Math.max(d.height+d3.event.dy,30);
                await update_positions();
            })
            .on("end", async function (d) {
                let data = await $.post("/websimgui", {
                        'fnc': 'set_model_size',
                        'data': JSON.stringify({
                            'agent': agent_data.id,
                            'model': d.id,
                            'width': d.width,
                            'height': d.height})});
                data = await decode_data(JSON.parse(data));
                await update_all_2(data);
            })
    }

    async onConnecting(){
        return d3.drag()
            .on("start", async function (d) {await connecting_start(this, d)})
            .on("drag", async function (d) {await connecting_drag(this, d)})
            .on("end", async function (d) {await connecting_end(this, d)});

        async function connecting_start(arrow, d){
            d3.select(".main").append("line")
                .classed("connecting_line", true)
                .style("stroke", "black")
                .style("stroke-dasharray", "5,5")
                .attr("x1", d.arrow.line_point_x)
                .attr("y1", d.arrow.line_point_y)
                .attr("x2", d.arrow.line_point_x)
                .attr("y2", d.arrow.line_point_y);

            let direction_1 = d3.select(arrow).data()[0].direction;

            d3.selectAll(".line").on("mouseover", null);


            d3.select(arrow)
                .classed("connecting_from", true);

            d3.selectAll('.arrow')
                .filter(function(d, i) {return d3.select(this).data()[0].direction !== direction_1;})
                .classed("port_selectable", true);

            /*
            d3.selectAll('.port_selectable')
                .filter(function(d, i) {return d.model.id === d3.select(".connecting_from").data()[0].model.id;})
                .classed("port_inselectable", true)
                .classed("port_selectable", false);
             */


            d3.selectAll('.port_selectable')
                .on("mouseover", function() { d3.select(this).classed("connecting_to", true);})
                .on("mouseout", function() { d3.select(this).classed("connecting_to", false);});
        }

        async function connecting_drag(arrow,d){
            if (d3.select(".connecting_to").empty()) {
                let pos = d3.mouse(arrow);
                d3.select(".connecting_line")
                    .attr("x2", pos[0])
                    .attr("y2", pos[1]);
            } else {
                d3.select(".connecting_line")
                    .attr("x2", d3.select(".connecting_to").data()[0].arrow.line_point_x)
                    .attr("y2", d3.select(".connecting_to").data()[0].arrow.line_point_y);
            }
        }

        async function connecting_end(arrow,d){
            d3.select(".connecting_line").remove();

            if (!d3.select(".connecting_to").empty()) {
                await connections.add(d3.select(".connecting_from"), d3.select(".connecting_to"));
            }

            d3.selectAll('.connecting_to').classed("connecting_to", false);
            d3.selectAll('.port_choice1').classed("port_choice1", false).classed("port", true);
            d3.selectAll('.port_inselectable').classed("port_inselectable", false).classed("port", true);
            d3.selectAll('.port_selectable').classed("port_selectable", false).classed("port", true);
            d3.selectAll('.port').on("mouseover", null).on("mouseout", null);

            d3.selectAll(".line").on("mouseover", function(d){d3.select(this).classed("line_hover",true);});


        }
    }
}