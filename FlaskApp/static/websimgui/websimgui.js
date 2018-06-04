
let agent_data;
let main;

let menu;
let connections;
let models;
let popup_addModel;
let popup_model;
let contextMenu;


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
    popup_addModel = new Popup_addModel(d3.select("#wsg"));
    popup_model = new Popup_model(d3.select("#wsg"));
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
    let data = await $.getJSON("/websimgui/data?agent=" + agent_id)
        .done(function() {})
        .fail(function() {})
        .always(function() {});
    agent_data = data;
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
        agent_data = data;
        if (rebuild){
            await build_all();
        } else {
            await update_all();
        }
    }
}



