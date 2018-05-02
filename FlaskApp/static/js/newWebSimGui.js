
window.onload = function() {

    agent_data = $.get("/websimgui/data",function(result){console.log(result)});

    d3.select("#working_field").append("svg")
        .classed("wsg", true)
        .attr("width", "100%")
        .attr("height", "100%");


    d3.select(".wsg").append("rect")
        .classed("zoomer", true)
        .attr("pointer-events", "all")
        .call(d3.zoom().scaleExtent([0.1, 8])
            .on("zoom", function () {main.attr("transform", d3.event.transform);}
            )
        );

    let main = d3.select(".wsg").append("g")
        .classed("main",true);



    update_models_elements(main);
    update_connections_elements(main);

    recalculate_properties();

    update_positions(main);
};

function decode_data(data){
    data.models = d3.entries(data.models);
    return data;
}

function encode_data(data){
    data.models = d3.nest()
        .key(function(d) { return d.id; })
        .rollup(function(v) { return v[0]; })
        .object(data.models);
    return data;
}



function update_models_elements(main){


    let models = main.selectAll(".model").data(agent_data.models);

    //exit
    models.exit().remove();

    //enter
    models = models.enter().append("g")
        .classed("model",true)
        .attr("id", function (d) { return d.id; });
    models.append("rect")
        .classed("box",true)
        .call(d3.drag()
            .on("start", function (d) {})
            .on("drag", function (d) {
                d.x = d.x + d3.event.dx;
                d.y = d.y + d3.event.dy;
                recalculate_properties();
                update_positions(main);
            })
            .on("end", function (d) {
                $.post("/websimgui", {
                        'model': d.id,
                        'function': 'set_model_pos',
                        'data': JSON.stringify(agent_data)},
                    function(result){
                        console.log(result)
                    });
            })
        );
    models.append("text")
        .classed("name",true)
        .attr("text-anchor", "middle")
        .attr("alignment-baseline", "central")
        .call(d3.drag()
            .on("start", function (d) {})
            .on("drag", function (d) {
                d.x = d.x + d3.event.dx;
                d.y = d.y + d3.event.dy;
                recalculate_properties();
                update_positions(main);
            })
            .on("end", function (d) {})
        );

    models.append("rect")
        .classed("sizer",true)
        .call(d3.drag()
            .on("start", function (d) {})
            .on("drag", function (d) {
                d.width = Math.max(d.width+d3.event.dx,30);
                d.height = Math.max(d.height+d3.event.dy,30);
                recalculate_properties();
                update_positions(main);
            })
            .on("end", function (d) {

            })
        );

    update_ports_elements("inputs");
    update_ports_elements("outputs");
}

function update_ports_elements(direction) {
    let models = d3.selectAll(".model");
    let rail = models.append("g")
        .classed(direction,true);

    let ports = rail.selectAll(".port").data(function (d) { return d[direction].ports });
    ports.exit().remove();
    ports = ports.enter().append("g")
        .classed("port", true)
        .attr("id", function (d) { return d.id; });
    ports.append("polyline")
        .classed("arrow", true)
        .call(connecting());
    ports.append("text")
        .classed("name", true);
}

function update_connections_elements(main){
    let connections = main.selectAll(".connection").data(agent_data.connections);

    //exit
    connections.exit().remove();

    //enter
    connections = connections.enter().append("g")
        .classed("connection",true)
        .attr("id", function (d) { return d.id; });
    connections.append("line")
        .classed("line",true);
}

function connecting(){
    return d3.drag()
        .on("start", function (d) {connecting_start(this, d)})
        .on("drag", function (d) {connecting_drag(this, d)})
        .on("end", function (d) {connecting_end(this, d)});

    function connecting_start(arrow, d){
        connecting_line = d3.select(".main").append("line")
            .classed("connecting_line", true)
            .style("stroke", "black")
            .style("stroke-dasharray", "5,5")
            .attr("x1", d.arrow.line_point_x)
            .attr("y1", d.arrow.line_point_y)
            .attr("x2", d.arrow.line_point_x)
            .attr("y2", d.arrow.line_point_y);

        let direction_1 = d3.select(arrow).data()[0].direction


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

    function connecting_drag(arrow,d){
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

    function connecting_end(arrow,d){
        d3.select(".connecting_line").remove();

        if (!d3.select(".connecting_to").empty()) {
            add_connection(1, 2);
        }

        d3.selectAll('.connecting_to').classed("connecting_to", false);
        d3.selectAll('.port_choice1').classed("port_choice1", false).classed("port", true);
        d3.selectAll('.port_inselectable').classed("port_inselectable", false).classed("port", true);
        d3.selectAll('.port_selectable').classed("port_selectable", false).classed("port", true);
        d3.selectAll('.port').on("mouseover", null).on("mouseout", null);


    }
}

function add_connection(port1, port2){
    if (false) {

        let input={};
        let output={};

        switch (d3.select(selection.parentNode).attr("class")){
            case 'inputs':
                input.port_id = selection.id;
                input.model_id = selection.parentElement.parentElement.id;
                output.port_id = d3.select(".port_choice1").attr("id");
                output.model_id = '';
                break;
            case 'outputs':
                input.port_id = d3.select(".port_choice1").attr("id");
                input.model_id = arrow.parentElement.parentElement.id;
                output.port_id = selection.id;
                output.model_id = selection.parentElement.parentElement.id;
                break;
            default:
                // errror
                break;
        }

        let new_connection = {'id': 'connection_10', 'input': input, 'output': output};

        agent_data.connections.push(new_connection);
        selection = null;
        update();
    }
}

function recalculate_properties() {
    for (let i_mod = 0; i_mod < agent_data.models.length; i_mod++) {
        let model = agent_data.models[i_mod];
        model.name = {};
        model.name.x = model.x + model.width / 2;
        model.name.y = model.y + model.height / 2;

        model.sizer = {};
        model.sizer.size = 10;
        model.sizer.x = model.x + model.width - model.sizer.size / 2;
        model.sizer.y = model.y + model.height - model.sizer.size / 2;

        let directions = ['inputs', 'outputs'];
        for (let i = 0; i < directions.length; i++) {
            let direction = directions[i];
            let dx = model.width / model[direction].ports.length;
            let x = model.x + dx / 2;
            let dy = model.height / model[direction].ports.length;
            let y = model.y + dy / 2;


            for (let i_in = 0; i_in < model[direction].ports.length; i_in++) {
                let port = model[direction].ports[i_in];
                port.direction = direction;
                port.model = {};
                port.model.id = model.id;
                port.text = {};

                switch (model[direction].orientation) {
                    case "left":
                        port.x = model.x;
                        port.y = y;
                        y += dy;
                        port.text.anchor = "start";
                        port.text.baseline = "central";
                        port.text.x = port.x + 4;
                        port.text.y = port.y;
                        break;
                    case "right":
                        port.x = model.x + model.width;
                        port.y = y;
                        y += dy;
                        port.text.anchor = "end";
                        port.text.baseline = "central";
                        port.text.x = port.x - 4;
                        port.text.y = port.y;
                        break;
                    case "top":
                        port.x = x;
                        x += dx;
                        port.y = model.y;
                        port.text.anchor = "middle";
                        port.text.baseline = "hanging";
                        port.text.x = port.x;
                        port.text.y = port.y + 4;
                        break;
                    case "bottom":
                        port.x = x;
                        x += dx;
                        port.y = model.y + model.height;
                        port.text.anchor = "middle";
                        port.text.baseline = "ideographic";
                        port.text.x = port.x;
                        port.text.y = port.y - 4;
                        break;
                }

                form = get_port_arrow_form(model[direction].orientation, direction, 10);

                port.arrow = {};
                port.arrow.points = "X1,Y1 X2,Y2 X3,Y3"
                    .replace("X1", form[0] + port.x)
                    .replace("Y1", form[1] + port.y)
                    .replace("X2", form[2] + port.x)
                    .replace("Y2", form[3] + port.y)
                    .replace("X3", form[4] + port.x)
                    .replace("Y3", form[5] + port.y);
                port.arrow.line_point_x = form[6] + port.x;
                port.arrow.line_point_y = form[7] + port.y;
            }
        }
    }

    for (let i_con = 0; i_con < agent_data.connections.length; i_con++) {
        let connections = agent_data.connections[i_con];
    }

    function get_port_arrow_form(orientation, direction, size) {
        let form = [[-size/1.5,0],[size/1.5,0],[0,size],[0,size]]; // top , out

        if (direction === 'inputs') { // top, out
            for (let i = 0; i < form.length-1; i++) {
                form[i][1] = size - form[i][1];
            }
        }
        let temp;
        for (let i = 0; i < form.length; i++) {
            switch (orientation) {
                case "left": // turn to left
                    temp = form[i][0];
                    form[i][0] = 0-form[i][1];
                    form[i][1] = 0-temp;
                    break;
                case "right": // turn to right
                    temp = form[i][0];
                    form[i][0] = form[i][1];
                    form[i][1] = temp;
                    break;
                case "bottom": // flip to bottom
                    form[i][0] = 0 - form[i][0];
                    form[i][1] = 0 - form[i][1];
                    break;
            }
        }
        return [form[0][0],form[0][1],form[1][0],form[1][1],form[2][0],form[2][1],form[3][0],form[3][1]];
        return form
    }
}

function update_positions(main){
    let models = main.selectAll(".model");

    models.select(".box")
        .attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; })
        .attr("width", function(d) { return d.width; })
        .attr("height", function(d) { return d.height; });

    models.select(".name")
        .attr("x", function(d) { return d.name.x; })
        .attr("y", function(d) { return d.name.y; })
        .text(function(d) { return d.name; });

    models.select(".sizer")
        .attr("x", function (d) { return d.sizer.x })
        .attr("y", function (d) { return d.sizer.y })
        .attr("width", function (d) { return d.sizer.size })
        .attr("height", function (d) { return d.sizer.size });

    let ports = main.selectAll(".port");

    ports.select(".name")
        .attr("x", function(d){ return d.text.x + 2; })
        .attr("y", function(d){ return d.text.y; })
        .text(function(d) { return d.name; })
        .attr("text-anchor", function(d) { return d.text.anchor})
        .attr("alignment-baseline", function(d) { return d.text.baseline});

    ports.select(".arrow")
        .attr("points", function(d){ return d.arrow.points; });

    let connections = main.selectAll(".connection");

    connections.select(".line")
        .attr("x1", function (d) {return d3.select("#" +d.input).data()[0].arrow.line_point_x})
        .attr("y1", function (d) {return d3.select("#" +d.input).data()[0].arrow.line_point_y})
        .attr("x2", function (d) {return d3.select("#" +d.output).data()[0].arrow.line_point_x})
        .attr("y2", function (d) {return d3.select("#" +d.output).data()[0].arrow.line_point_y});
}




