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
    await mo_diag.update();
    await mp_diag.update();

    await set_updater();
};

async function set_updater() {
    clearInterval(update_interval);
    update_interval = setInterval(await async function() {
        await mo_diag.update();
    }, 2*1000);
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

