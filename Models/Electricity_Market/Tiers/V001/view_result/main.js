let run = 0;
let menu;
let diag;
let diag_tiers_try;
let diag_int_try;
let update_speed = 0.2;
let update_interval_time = 1;
let update_interval;


window.onload = async function() {

    // ET and NT Tiers
    let d3Tiers = d3.select("#d3_tiers");
    diag_tiers_try = new EN_Tiers(d3Tiers);

    // Diagram
    let d3d = d3.select("#d3_timeseries");
    //d3d.style("color", "blue");
    diag = new Diagram(d3d);

    // Integrated
    let d3Int = d3.select("#d3_integrated");
    diag_int_try = new Integrated(d3Int);

    // Buttons
    let d3_button = d3.select("#d3_buttons");
    buttons = new Buttons(d3_button);

    // menu
    menu = new Menu(d3.select("#menu"));



    await updateAll(0);

    await set_updater();

};

async function updateAll(updateSpeed) {
    await menu.updateData();
    menu.updateMenu(updateSpeed);

    await buttons.updateData();
    buttons.updateMenu(updateSpeed);

    await diag.updateData();
    try {
        diag.updateView(updateSpeed);
    } catch (e) {
        console.log("no view update - wait for data")
    }

    await diag_tiers_try.updateData();
    diag_tiers_try.updateView(updateSpeed);

    await diag_int_try.updateData();
    diag_int_try.updateView(updateSpeed);
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
