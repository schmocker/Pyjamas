let run = 0;
let menu;
let diag;
let update_speed = 0.2;
let update_interval_time = 1;
let update_interval;


window.onload = async function() {
    // Diagram
    let d3d = d3.select("#d3_drawing");
    //d3d.style("color", "blue");
    diag = new Diagram(d3d);

    // menu
    menu = new Menu(d3.select("#menu"));



    await updateAll(0);

    await set_updater();

};

async function updateAll(updateSpeed) {
    await menu.updateData();
    menu.updateMenu(updateSpeed);

    await diag.updateData();
    try {
        diag.updateView(updateSpeed);
    } catch (e) {
        console.log("no view update - wait for data")
    }
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

async function get(data_dict){
    let query_name = 'get_mu_results';
    let data = await $.get("/websimgui", {
        'fnc': query_name,
        'data': JSON.stringify(data_dict)});
    if (data === "false"){
        alert('GET request returned "false", check the request for the query "' + query_name + '"!');
        return false
    } else {
        return data;
    }
}

d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};
