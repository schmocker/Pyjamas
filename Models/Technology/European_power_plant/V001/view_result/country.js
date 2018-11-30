class Country {
    constructor(parent, geo_path) {
        this.parent = parent;
        this.geo_path = geo_path;
        let obj = this;
        this.run = 0;

        this.UCTE_ISO3 =  ["BEL","BIH","BGR","DNK","DEU","FRA","GRC","ITA","HRV","LUX","FYR","MNE","NLD","AUT","POL","PRT","ROU","CHE","SCG","SVK","SVN","ESP","CZE","HUN","MKD","SRB","XKX"];


        this.tooltip = new ToolTip(parent.svg);

        this.g = this.parent.g.append('g')
            .attr('id', 'countries');

    }

    set data(data) {
        this.items = this.g.selectAll('.country').data(data.features);
        this._exit();
        this._enter();
        this.items = this.g.selectAll('.country');
        this._update();
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let obj = this;

        let new_items = this.items.enter();
        new_items.append("path")
            .attr("d", this.geo_path)
            .attr("class", function(d) {
                let classes = "country";
                classes += " " + d.properties.continent;
                classes += (obj.UCTE_ISO3.includes(d.properties.iso_a3)) ? " UCTE" : "";
                return classes;
            })
            .on("mouseover", function(d) {
                let ucte;
                if (obj.UCTE_ISO3.includes(d.properties.iso_a3)){
                    ucte = "is a UCTE country";
//                    ucte = d.properties.name + " is a UCTE country";
                } else {
                    ucte = "is not a UCTE country";
//                    ucte = d.properties.name + " is not a UCTE country";
                }
                obj.tooltip.show(d.properties.name, ucte); })
            .on("mouseout", function() { obj.tooltip.hide(); });
    }

    _update() {
        let obj = this;

        /*
        d3.selectAll(".country").each(function(d, i) {
           d3.select(this).moveToFront();
        });
        */

    }
}


class ToolTip {
    constructor(parent) {
        this.parent = parent;

        this.g = this.parent.append("g")
            .attr("class", "tooltip")
            .style("opacity", 0.8)
            .style("display", "none");

        this.rect = this.g.append("rect");
        this.val_c = this.g.append("text")
            .attr("id", "val_c");
        this.val_UCTE = this.g.append("text")
            .attr("id", "val_UCTE");

        this.padding = 10;
    }

    show(value_c, value_UCTE){
        this.g.moveToFront();

        let size = parseInt(this.g.style("font-size"));
        this.val_c.text(value_c)
            .attr("y",size);
        this.val_UCTE.text(value_UCTE)
            .attr("y",2.5*size);

        let height = 2.5*size;
        let w1 = this.val_c.node().clientWidth;
        let w2 = this.val_UCTE.node().clientWidth;
        let width = Math.max(w1,w2);

        this.rect
            .attr("x",-this.padding)
            .attr("y",-this.padding)
            .attr("width", width+2*this.padding)
            .attr("height", height+2*this.padding);

        let x_scale = 100;
        let y_scale = 100;
        this.g
            .attr("transform", "translate(" + (x_scale-width/2) + "," + (y_scale-10-this.padding-height) + ")")
            .transition().duration(this.updateSpeed)
            .style("display", "inline");
    }

    hide(){
        this.g.transition()
            .duration(this.updateSpeed)
            .style("display", "none");
    }
}