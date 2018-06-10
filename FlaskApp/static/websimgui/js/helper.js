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