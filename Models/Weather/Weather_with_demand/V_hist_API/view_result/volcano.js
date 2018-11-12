class Volcano {
    constructor(parent) {
        this.parent = parent;
        let obj = this;
        this.run = 0;

        this.g = this.parent.g.append('g')
            .attr('id', 'volcanos');

    }

    set data(data) {
        let volcano = this.parent.data_volcano;
        this.items = this.g.selectAll('.volcano').data(d3.contours()
            .size([volcano.width, volcano.height])
            .thresholds(d3.range(90, 195, 5))
            (volcano.values));
        this._exit();
        this._enter();
        this.items = this.g.selectAll('.volcano');
        this._update();
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let obj = this;

        let i0 = d3.interpolateHsvLong(d3.hsv(120, 1, 0.65), d3.hsv(60, 1, 0.90));
        let i1 = d3.interpolateHsvLong(d3.hsv(60, 1, 0.90), d3.hsv(0, 0, 0.95));
        let interpolateTerrain = function(t) { return t < 0.5 ? i0(t * 2) : i1((t - 0.5) * 2); };
        let color = d3.scaleSequential(interpolateTerrain).domain([90, 190]);

        let new_items = this.items.enter();
        new_items.append("path")
            .attr("d", d3.geoPath(d3.geoIdentity().scale(obj.parent.width / obj.parent.data_volcano.width)))
            .attr("fill", function(d) { return color(d.value); });
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
