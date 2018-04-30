class Rail {
    constructor(model, direction, orientation, ports_obj){
        this.direction = direction; // in || out
        this.orientation = orientation; // left || right

        this.numOfPorts = 0;

        this.model = model;
        this.ports = {};

        for (let port_id in ports_obj){
            if (!ports_obj.hasOwnProperty(port_id)) continue;
            this.ports[port_id] = new Port(this, port_id, ports_obj[port_id]);
            this.numOfPorts++;
        }

    }

    updatePosition(){
        let model_pos = this.model.position;
        let x = model_pos[this.orientation];

        let dy = model_pos["height"]/(this.numOfPorts);
        let y = model_pos["top"] + dy/2;

        for (let port_id in this.ports){
            this.ports[port_id].updatePosition(x,y);
            y += dy;
        }
    }
}