class Popup_model extends Popup{
    constructor(parent) {
        super(parent, "model_documentation");
    }

    async setContent(model_id){
        this.content =  await $.get("/websimgui", {
            'agent': agent_data.id,
            'fnc': 'get_model_description',
            'data': JSON.stringify({
                'model': model_id
            })});
    }

}