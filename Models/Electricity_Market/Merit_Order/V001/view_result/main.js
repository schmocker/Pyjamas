let run = 0;

let powerplants_run = 0;
let result;

let update_interval;

let values;

let menu;
let mo_diag;
let mp_diag;


let i_dn = 0;
let i_ts = 0;
let times = null;
let dns = null;


window.onload = async function() {
    menu = new Menu(d3.select(".menu"));
    mo_diag = new MeritOrderDiagram(d3.select(".mo_diag"));
    mp_diag = new MarketPriceDiagram(d3.select(".mp_diag"));

    await menu.update();

    await updateAll(0);

    await set_updater();
};

async function updateAll(updateSpeed) {
    await mo_diag.updateData();
    await mp_diag.updateData();

    mo_diag.updateView(updateSpeed);
    mp_diag.updateView(updateSpeed);
}

async function set_updater() {
    clearInterval(update_interval);
    update_interval = setInterval(await async function() {
        await updateAll(500);
    }, 1*1000);
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

d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};
d3.selection.prototype.moveToBack = function() {
    return this.each(function() {
        let firstChild = this.parentNode.firstChild;
        if (firstChild) {
            this.parentNode.insertBefore(this, firstChild);
        }
    });
};

