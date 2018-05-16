
let agent_data;
let main;

let connections;
let models;
let popup_addModel;

window.onload = async function() {
    connections = new Connections();
    models = new Models();


    d3.select("#wsg").append("svg")
        .attr("id", "wsg_drawing");


    d3.select("#wsg").append("div")
        .attr("id", "wsg_menu");


    popup_addModel = new Popup_addModel(d3.select("#wsg"));

    d3.select("#wsg_menu").append("img")
        .attr("src","static/images/icons/arrows_in.png")
        .attr("width", 30)
        .attr("height", 30)
        .on("click", async function() {
            full_screen();
        });

    d3.select("#wsg_menu").append("img")
        .attr("src","static/images/icons/plus.png")
        .attr("width", 30)
        .attr("height", 30)
        .on("click", async function() {
            await popup_addModel.popup()
        });


    d3.select("#wsg_drawing").append("rect")
        .classed("zoomer", true)
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", "none")
        .attr("pointer-events", "all")
        .call(await onZoom());

    main = d3.select("#wsg_drawing").append("g")
        .classed("main",true);
    await update_all();

    d3.select('body').append('div')
        .attr('class', 'context-menu');

    // close menu
    d3.select('body').on('click.context-menu', function() {
        d3.select('.context-menu').style('display', 'none');
    });



// When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        let modal = document.getElementById('myModal');
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
};



async function full_screen() {
    let isfullscreen = d3.select("#wsg").classed("full-screen");
    let arrow = isfullscreen ? "in" : "out";
    d3.select("#btn_fullscreen").attr("src","static/images/icons/arrows_"+arrow+".png");
    d3.select("#wsg").classed("full-screen",!isfullscreen);
}

async function update_all(){
    await get_data();



    await models.update();
    await connections.update();
    await update_positions();
    console.log("UPDATE DONE")
}
async function update_all_2(data){
    agent_data = data;

    await models.update();
    await connections.update();
    await update_positions();

    console.log("UPDATE DONE")
}

async function get_data(){
    let url = new URL(document.URL);
    let agent_id = url.searchParams.get("agent_id");
    agent_data = await $.getJSON("/websimgui/data?agent_id=" + agent_id, function( data ) {
        data.models = d3.values(data.models);
        $.each(data.models, function( index, value ) {
            value.inputs.ports = d3.values(value.inputs.ports);
            value.outputs.ports = d3.values(value.outputs.ports);
        });
        data.connections = d3.values(data.connections);
        return data;
    })
        .done(function() {console.log( "success" );})
        .fail(function() {console.log( "error" );})
        .always(function() {console.log( "complete" );});
}

async function decode_data(data){
    data.models = d3.values(data.models);
    $.each(data.models, function( index, value ) {
        value.inputs.ports = d3.values(value.inputs.ports);
        value.outputs.ports = d3.values(value.outputs.ports);
    });
    data.connections = d3.values(data.connections);
    return data;
}

async function encode_data(data){
    //
}

async function update_connections_elements(){
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
        .on("contextmenu", await onContextMenu(menu));
}

async function onZoom() {
    return d3.zoom().scaleExtent([0.1, 8])
        .on("zoom", function (d) {
            main.attr("transform", d3.event.transform);
        })
}

async function recalculate_properties() {
    for (let i_mod = 0; i_mod < agent_data.models.length; i_mod++) {
        let model = agent_data.models[i_mod];
        model.name_pos = {};
        model.name_pos.x = model.x + model.width / 2;
        model.name_pos.y = model.y - 4;
        // model.name_pos.y = model.y + model.height / 2;

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

                form = get_port_arrow_form(model[direction].orientation, direction, 15);

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

async function update_positions(){
    await recalculate_properties();
    models.update_position();
    connections.update_position();
}

onContextMenu = async function (menu, openCallback) {

    // this gets executed when a contextmenu event occurs
    return await async function(data, index) {
        console.log("context menu triggerd");

        let elm = this;

        d3.selectAll('.context-menu').html('');
        let list = d3.selectAll('.context-menu').append('ul');
        list.selectAll('li').data(menu).enter()
            .append('li')
            .html(function(d) {return d.title;})
            .on('click', async function(d, i) {
                await d.action(elm, data, index);
                d3.select('.context-menu').style('display', 'none');
            });

        // the openCallback allows an action to fire before the menu is displayed
        // an example usage would be closing a tooltip
        if (openCallback) openCallback(data, index);

        // display context menu
        d3.select('.context-menu')
            .style('left', (d3.event.pageX - 2) + 'px')
            .style('top', (d3.event.pageY - 2) + 'px')
            .style('display', 'block');

        d3.event.preventDefault();
    };
};

