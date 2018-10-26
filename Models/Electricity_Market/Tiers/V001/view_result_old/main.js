let run = 0;
let menu;
let diag;
let diag_tP;
let update_speed = 0.2;
let update_interval_time = 1;
let update_interval;


window.onload = async function() {

    // menu
    menu = new Menu(d3.select("#menu"));



    // Diagram
    let d3d = d3.select("#d3_drawing");
    d3d.style("background-color", "red");
    let d3d_tP = d3.select("#d3_drawing_tP");
    d3d_tP.style("background-color", "white");

    diag = new Diagram(d3d);
    diag_tP = new Diagram_tP(d3d_tP);

    await updateAll(0);

    await set_updater();

};

async function updateAll(updateSpeed) {
    log('update');

    await menu.updateData();
    menu.updateMenu(updateSpeed);

    await diag.updateData();
    diag.updateRects(updateSpeed);

    await diag_tP.updateData();
    diag_tP.updateView(updateSpeed);
}


async function set_updater() {
    clearInterval(update_interval);
    update_interval = setInterval(await async function() {
        await updateAll(update_speed*1000);
    }, update_interval_time * 1000);
}

function log(text) {
    console.log(text)
}


async function get(query_name, data_dict){
    let data = await $.get("/websimgui", {
        'fnc': query_name,
        'data': JSON.stringify(data_dict)});
    if (data === "false"){
        return null
    } else {
        return JSON.parse(data);
    }
}
