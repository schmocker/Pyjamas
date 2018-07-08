$.ajaxSetup({
    timeout:1000 // in milliseconds
});

async function post(fnc_str, data_dict, rebuild){

    data_dict['agent_id'] = agent_data.id;
    let data = await $.post("/websimgui", {
        'fnc': fnc_str,
        'data': JSON.stringify(data_dict),
        timeout: 1000
    });

    try {
        data = JSON.parse(data);
        if (data === true) {
        } else if ("error" in data){
            alert(data.error);
        } else {
            agent_data = data;
            if (rebuild){
                await build_all();
            } else {
                await update_all();
            }
        }
    } catch (e) {
        alert(e.message);
    }
    return false;
}

async function get(query_name, data_dict){
    let data = await $.get("/websimgui", {
        'agent': agent_data.id,
        'fnc': query_name,
        'data': JSON.stringify(data_dict)});
    try {
        data = JSON.parse(data);
        if (data){
            if ("error" in data){
                alert(data.error);
            } else {
                return data;
            }
        } else {
            log('no data received with GET request: '+query_name);
        }
    } catch(e) {
        alert(e.message);
    }
    return false;
}