class Powerplant {
    constructor(parent, projection) {
        this.parent = parent;
        this.projection = projection;
        let obj = this;
        this.run = 0;

        //this.zoom = new Zoom(this.parent);
        //this.tooltip = new ToolTip(this.parent);

        this.pp_g = this.parent.g.append('g')
            .attr('id', 'powerplants')
            .attr('class', 'circles');
    }

    set data(data) {
        this.items = this.pp_g.selectAll('.circles').data(data);
        this._exit();
        this._enter();
        this.items = this.pp_g.selectAll('.circles');
        this._update();
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let obj = this;

        let new_items = this.items.enter();
        new_items.append("circle")
            .attr("r", "4px")
            .attr("cx", function (d) {return obj.projection([d.long, d.lat])[0]})
            .attr("cy", function (d) {return obj.projection([d.long, d.lat])[1]})
            .style("stroke", "white")
            .style("fill", "white");

//            .attr("cx", function (d) {return obj.projection(d.long)})
//            .attr("cy", function (d) {return obj.projection(d.lat)});

    }

    _update() {
        let obj = this;



    }
}

