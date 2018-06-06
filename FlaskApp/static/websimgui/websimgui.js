
let agent_data;
let main;

let menu;
let connections;
let models;
let popup_addModel;
let popup_model_docu;
let contextMenu;
let popup_model_properties_view;
let popup_model_results_view;

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




    // Extras
    popup_addModel =                new Popup_addModel(d3.select("#wsg"));
    popup_model_docu =              new Popup_model_docu(d3.select("#wsg"));
    popup_model_properties_view =   new Popup_model_properties_view(d3.select("#wsg"));
    popup_model_results_view =      new Popup_model_results_view(d3.select("#wsg"));
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

async function get_data(){
    let url = new URL(document.URL);
    let agent_id = url.searchParams.get("agent");
    let data = await $.getJSON("/websimgui/data?agent=" + agent_id);


    await setData(data);
}

async function post(fnc_str, data_dict, rebuild){
    data_dict['agent'] = agent_data.id;
    let data = await $.post("/websimgui", {
        'fnc': fnc_str,
        'data': JSON.stringify(data_dict)
    });
    data = JSON.parse(data);
    if (data === false){
        alert('POST request returned "false", check the request for the function "' + fnc_str + '"!');
    } else {
        await setData(data);
        if (rebuild){
            await build_all();
        } else {
            await update_all();
        }
    }
}
async function get(query_name, data_dict){
    let data = await $.get("/websimgui", {
        'agent': agent_data.id,
        'fnc': query_name,
        'data': JSON.stringify(data_dict)});
    if (data === "false"){
        alert('GET request returned "false", check the request for the query "' + query_name + '"!');
        return false
    } else {
        return data;
    }
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

