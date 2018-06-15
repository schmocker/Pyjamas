
let agent_data;
let main;

let menu;
let connections;
let models;
let popup_addModel;
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

    menu = new Menu(d3.select("#wsg"));


    main = d3.select("#wsg_drawing").append("g")
        .classed("main",true);


    await update_all_models();
    view = new View(d3.select("#wsg"));

    // Extras
    popup_addModel =                new Popup_addModel(d3.select("#wsg"));
    contextMenu =                   new ContextMenu(d3.select("#wsg"));



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

async function update_all_models(){
    all_models = await $.get("/websimgui", {
        'fnc': 'get_model_selection',
        'data': JSON.stringify({})
    });
    all_models = JSON.parse(all_models);
}

async function get_data(){
    let url = new URL(document.URL);
    let agent_id = url.searchParams.get("agent");
    //let data = await $.getJSON("/websimgui/data?agent=" + agent_id);

    let data = await $.get("/websimgui", {
        'agent': agent_id,
        'fnc': 'get_agent',
        'data': JSON.stringify({})});
    data = JSON.parse(data);


    await setData(data);
}



async function setData(data) {
    let models_used = data.model_used;
    for (let i = 0; i < models_used.length; i++) {
        let model_used = models_used[i];
        let docks = model_used.model.info.docks;
        for (let j = 0; j < docks.length; j++) {
            let direction = docks[j].direction;
            let orientation = model_used[direction+"_orientation"];
            if (orientation != null) {
                data.model_used[i].model.info.docks[j].orientation = orientation;
            }
        }
    }

    agent_data = data
}

