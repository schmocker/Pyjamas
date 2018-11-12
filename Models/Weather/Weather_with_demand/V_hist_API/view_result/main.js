let run = 0;
let d_map;
let menu;
let timemenu;
let update_speed = 0.2;
let update_interval_time = 5;
let update_interval;

window.onload = async function(){

    // Map
    let d3map = d3.select("#map");
    d_map = new W_map(d3map);

    // Menu
    let d3menu = d3.select("#menu");
    menu = new Menu(d3menu);

    // Menu
    let d3menutime = d3.select("#menu_time");
    timemenu = new MenuTime(d3menutime);

    await updateAll(0);

    await set_updater();


};

async function updateAll(updateSpeed){
    await menu.updateData();
    menu.updateMenu(updateSpeed);

    await timemenu.updateData();
    timemenu.updateMenuTime(updateSpeed);

    await d_map.updateData();
    d_map.updateView(updateSpeed);
}

async function set_updater(){
    clearInterval(update_interval);
    update_interval = setInterval(await async function(){
        await updateAll(update_speed*1000);
    }, update_interval_time*1000);
}


async function post(fnc_str, data_dict){
    let data = await $.post("/websimgui", {
        'fnc': fnc_str,
        'data': JSON.stringify(data_dict)
    });
    data = JSON.parse(data);
    if (data === "false"){
        alert('POST request returned "false", check the request for the function "' + fnc_str + '"!');
        return false
    } else {
        return data;
    }
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

d3.selection.prototype.moveToBack = function() {
    return this.each(function() {
        var firstChild = this.parentNode.firstChild;
        if (firstChild) {
            this.parentNode.insertBefore(this, firstChild);
        }
    });
};


















