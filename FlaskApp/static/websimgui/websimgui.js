
let agent_data;
let main;

let connections;
let models;
let contextMenu;
let view;
let all_models;

window.onload = async function() {
    await get_data();

    models = new Models();
    connections = new Connections();


    d3.select("#wsg").append("svg")
        .attr("id", "wsg_drawing")
        .call(d3.zoom().scaleExtent([0.1, 8])
            .on("zoom", function(d){
                main.attr("transform", d3.event.transform);
            })
        )
        .on("dblclick.zoom", null);


    main = d3.select("#wsg_drawing").append("g")
        .classed("main",true);


    view = new View(d3.select("#wsg"));

    // Extras
    contextMenu = new ContextMenu(d3.select("#wsg"));



    await build_all();
};

function log(d) { console.log(d); }



async function build_all(){
    await models.build();
    await connections.build();
    console.log("BUILD DONE")
}

async function update_all(){

    await models.update();
    await connections.update();


    console.log("UPDATE DONE")
}


async function get_data(){
    let url = new URL(document.URL);
    let agent_id = url.searchParams.get("agent");

    let data = await $.get("/websimgui", {
        'agent': agent_id,
        'fnc': 'get_agent',
        'data': JSON.stringify({})});
    data = JSON.parse(data);


    agent_data = data;
}

