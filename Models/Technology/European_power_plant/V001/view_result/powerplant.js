class Powerplant {
    constructor(parent, projection) {
        this.parent = parent;
        this.projection = projection;
        let obj = this;
        this.run = 0;

        this.tooltip_pp = new ToolTip_PP(parent.svg);

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
            .style("fill", "white")
            .on("mouseover", function(d) {
                let kw_bez = d.kw_bezeichnung;
                let p = 1;
                let p_info = "current power: " + p.toString() + "W?";
                let posx = obj.projection([d.long, d.lat])[0];
                let posy = obj.projection([d.long, d.lat])[1];
                obj.tooltip_pp.show(kw_bez, p_info, posx, posy); })
            .on("mouseout", function() { obj.tooltip_pp.hide(); });
    }

    _update() {
        let obj = this;

    }

}

class ToolTip_PP {
    constructor(parent) {
        this.parent = parent;

        this.g = this.parent.append("g")
            .attr("class", "tooltip_pp")
            .style("opacity", 0);

        this.rect = this.g.append("rect");
        this.kw_bez = this.g.append("text")
            .attr("id", "kb_bez");
        this.val_p = this.g.append("text")
            .attr("id", "val_p");

        this.padding = 10;
    }

    show(kw_bez, value_p, posx, posy){
        this.g.moveToFront();

        let size = parseInt(this.g.style("font-size"));
        this.kw_bez.text(kw_bez)
            .attr("y",size);
        this.val_p.text(value_p)
            .attr("y",2.5*size);

        let height = 2.5*size;
        let w1 = this.kw_bez.node().clientWidth;
        let w2 = this.val_p.node().clientWidth;
        let width = Math.max(w1,w2);

        this.rect
            .attr("x",-this.padding)
            .attr("y",-this.padding)
            .attr("width", width+2*this.padding)
            .attr("height", height+2*this.padding);

        this.g
            .attr("transform", "translate(" + (posx-width/2) + "," + (posy-10-this.padding-height) + ")")
            .transition().duration(this.updateSpeed)
            .style("opacity", .9);
    }

    hide(){
        this.g.transition()
            .duration(this.updateSpeed)
            .style("opacity", 0);
    }
}