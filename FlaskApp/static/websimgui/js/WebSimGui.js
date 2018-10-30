// import {Models} from "./Models";
// import {Connections} from "./Connections";
// import {View} from "./View";
// import {ContextMenu} from "./ContextMenu";

// export

class WebSimGui{
    constructor(div_id){
        let url = new URL(document.URL);
        this.agent_id = url.searchParams.get("agent");

        this.data = null;

        this.wsg = d3.select(div_id);

        this.svg = this.wsg.append("svg")
            .attr("id", "wsg_drawing");



        this.main = d3.select("#wsg_drawing").append("g").classed("main",true);

        let obj = this;
        this.svg.call(d3.zoom().scaleExtent([0.1, 8]).on("zoom", function(){
            obj.main.attr("transform", d3.event.transform);
        }));
        this.svg.on("dblclick.zoom", null);


        this.models = null;
        this.connections = null;
        this.view = null;
        this.contextMenu = null;
    }

    async start(){
        this.data = await this.get_data();

        this.models = new Models(this);
        this.connections = new Connections(this);
        this.view = new View(this);
        this.contextMenu = new ContextMenu(this.wsg);

        await this.build_all();
    }

    async build_all(){
        this.data = await this.get_data();

        await this.models.build();
        await this.connections.build();

        console.log("BUILD DONE")
    }

    async get_data(){
        let data = await $.get("/websimgui", {
            'agent': this.agent_id ,
            'fnc': 'get_agent',
            'data': JSON.stringify({})});
        return JSON.parse(data);
    }

    async update_all(){
        await this.models.update();
        await this.connections.update();


        console.log("UPDATE DONE")
    }

    async post(fnc_str, data_dict, rebuild){

        try {
            data_dict['agent_id'] = this.agent_id;
            let data = await $.post("/websimgui", {
                'fnc': fnc_str,
                'data': JSON.stringify(data_dict)
            });
            data = JSON.parse(data);
            if (data === true) {
            } else if ("error" in data){
                console.warn(data.error);
            } else {
                this.data = data;
                if (rebuild){
                    await this.build_all();
                } else {
                    await this.update_all();
                }
            }
        } catch (e) {
            console.warn(e.message);
        }
        return false;
    }
    async get(query_name, data_dict){
        let data = await $.get("/websimgui", {
            'agent': this.agent_id,
            'fnc': query_name,
            'data': JSON.stringify(data_dict)});
        try {
            data = JSON.parse(data);
            if (data){
                if ("error" in data){
                    console.warn(data.error);
                } else {
                    return data;
                }
            } else {
                console.warn('no data received with GET request: '+query_name);
            }
        } catch(e) {
            alert(e.message);
        }
        return false;
    }
}
