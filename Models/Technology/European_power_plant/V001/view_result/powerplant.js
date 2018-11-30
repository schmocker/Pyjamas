class Powerplant {
    constructor(parentObj, parentNode, projection, tooltip) {
        this.parentObj = parentObj;
        this.parentNode = parentNode;
        this.projection = projection;
        this.tooltip = tooltip;

        let obj = this;
        this.run = 0;

        this.Node = this.parentNode.append('g')
            .attr('id', 'powerplants')
            .attr('class', 'circles');
   }

    set data(data) {
        this.items = this.Node.selectAll('circle').data(data);
        this._exit();
        this._enter();
        this.items = this.Node.selectAll('circle');
        this._update();
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let obj = this;

        let new_items = this.items.enter();
        new_items.append("circle")
            .on("mouseover", function(d) {
                let kw_bez = d.kw_bezeichnung;
                let p = d.p_inst/1E9;
                p = Math.round(p*100)/100;
                let p_info = "installed power: " + p.toString() + " GW";
                let posx = obj.projection([d.long, d.lat])[0];
                let posy = obj.projection([d.long, d.lat])[1];
                obj.tooltip.show(kw_bez, p_info, posx, posy); })
            .on("mouseout", function() { obj.tooltip.hide(); });
    }

    _update() {
        let obj = this;

        this.items
            .attr("r", function (d) {return 5*Math.sqrt(d.p_inst/1E9)})
            .attr("cx", function (d) {return obj.projection([d.long, d.lat])[0]})
            .attr("cy", function (d) {return obj.projection([d.long, d.lat])[1]})
            .style("stroke", "white")
            .style("fill", "white")

        /*
        let items = this.pp_g.selectAll(".circles").selectAll("circle")
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
        */
    }

}

class ToolTip_PP {
    constructor(parentObj, parentNode) {
        this.parentObj = parentObj;
        this.parentNode = parentNode;

        this.Node = this.parentNode.append("g")
            .attr("class", "tooltip_pp")
            .style("opacity", 0.8)
            .style("display", "none");

        this.rect = this.Node.append("rect");
        this.kw_bez = this.Node.append("text")
            .attr("id", "kb_bez");
        this.val_p = this.Node.append("text")
            .attr("id", "val_p");

        this.padding = 10;
    }

    show(kw_bez, value_p, posx, posy){
        this.Node.moveToFront();

        let size = parseInt(this.Node.style("font-size"));
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

        this.Node
            .attr("transform", "translate(" + (posx-width/2) + "," + (posy-10-this.padding-height) + ")")
            .transition().duration(this.updateSpeed)
            .style("display", "inline");
    }

    hide(){
        this.Node.transition()
            .duration(this.updateSpeed)
            .style("display", "none");
    }
}