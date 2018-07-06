async function remove_agent(id) {
    await $.post("/agents", {'fnc': 'remove_agent', 'agent_id': id});
    location.reload();
}

function edit_agent(id) {
    $(location).attr('href', '/agents?agent=' + id );
}

async function duplicate(id, name) {
    name = name + ' copy';
    await $.post("/agents", {'fnc': 'copy_agent', 'agent_name': name, 'agent_id': id});
    location.reload();
}


async function rename(id, name){
    let name2 = prompt("Please enter new agent name", name);
    if (name2 && name2 !== ""){
        name = name2;
        await $.post("/agents", {'fnc': 'rename_agent', 'agent_name': name, 'agent_id': id});
        location.reload();
    }
}