/*$("add_agent").addEventListener("submit", await myFunction());
  async function myFunction() {
      alert("The form was submitted");
  }*/


async function remove_agent(id) {
    await $.post("/agents", {'fnc': 'remove_agent', 'agent_id': id});
    location.reload();
}

function edit_agent(id) {
    $(location).attr('href', '/agents?agent=' + id );
}