class Meteo {
    constructor(parent, projection) {
        this.parent = parent;
        this.projection = projection;
        let obj = this;
        this.run = 0;

        this.meteo_g = this.parent.g.append('g')
            .attr('id', 'meteos');

        this.legend = new Legend(this.parent.g, this.parent.width*0.91, 20, this);

        this.information = new Information(this.parent.g);

    }

    set data(data) {
        this.meteo_data = data;
        this.items = this.meteo_g.selectAll('.meteo').data(
            d3.contours()
                .size([this.meteo_data.width, this.meteo_data.height])
                .thresholds(this.meteo_data.scale.threshold)
                //.thresholds(d3.range(0,100,5))
                (this.meteo_data.values)
        );
        this._exit();
        this._enter();
        this.items = this.meteo_g.selectAll('.meteo');
        this._update();
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let obj = this;

        this.items.enter().append("path").classed("meteo", true);
    }

    _update() {
        let obj = this;

        this.meteo_g.moveToBack();

        // projection
        let coord_topleft = obj.projection([d3.min(this.meteo_data.lon), d3.max(this.meteo_data.lat)]);
        let coord_topright = obj.projection([d3.max(this.meteo_data.lon), d3.max(this.meteo_data.lat)]);
        let coord_bottomleft = obj.projection([d3.min(this.meteo_data.lon), d3.min(this.meteo_data.lat)]);
        let coord_width = coord_topright[0] - coord_topleft[0];
        let coord_height = coord_bottomleft[1] - coord_topleft[1];

        let scale_x = coord_width / this.meteo_data.width;
        let scale_y = coord_height / this.meteo_data.height;
        function scale (scaleFactor_x, scaleFactor_y) {
            return d3.geoTransform({
                point: function(x, y) {
                    this.stream.point(x * scaleFactor_x, y  * scaleFactor_y);
                }
            });
        }

        let color = d3.scaleSequential(this.meteo_data.scale["col_scheme"]);
        let scale_a = this.meteo_data.scale["col_scale_prop"][0];
        let scale_b = this.meteo_data.scale["col_scale_prop"][1];

        this.items
            .attr("d", d3.geoPath().projection(scale(scale_x, scale_y)))
            .attr("fill", function(d) { return color(d.value*scale_a+scale_b); })
            .attr("transform", "translate(" + coord_topleft[0].toString() + "," + coord_topleft[1].toString() + ")")
            .style("opacity", 0.3);

        // Time and meteo information
        this.information.show(this.meteo_data.info.info_time, this.meteo_data.info.info_meteo)

        // Legend

        let data_levels = this.parent.g.selectAll(".meteo").selectAll("path")._parents
            .map(function (c) {return {
                levels: c.__data__.value,
                colors: c.attributes.fill.value}});
        //let data_colors = ["#8B0000", "#FFFFFF", "#0000CD"];
        this.legend.data = data_levels;

    }

}



class Information {
    constructor(parent) {
        this.parent = parent;
        let obj = this;
        this.run = 0;

        this.g = this.parent.append("g")
            .attr("class", "information");

        this.rect = this.g.append("rect");
        this.info_time = this.g.append("text")
            .attr("id", "info_time");
        this.info_meteo = this.g.append("text")
            .attr("id", "info_meteo");

        this.padding = 10;
    }

    show(info_time, info_meteo) {
        this.g.moveToFront();

        let size = parseInt(this.g.style("font-size"));
        this.info_time.text(info_time)
            .attr("y", size);
        this.info_meteo.text(info_meteo)
            .attr("y", 2.5 * size);

        let height = 2.5 * size;

        let wx = this.info_time.node().clientWidth;
        let wy = this.info_meteo.node().clientWidth;
        let width = Math.max(wx, wy);

        this.rect
            .attr("x", -this.padding)
            .attr("y", -this.padding)
            .attr("width", width + 2 * this.padding)
            .attr("height", height + 2 * this.padding);

        this.g
            .attr("transform", "translate(" + (100) + "," + (100) + ")")
            .transition().duration(this.updateSpeed)
            .style("opacity", .9);

    }
}

class Legend {
    constructor(parent, x, y, this_parent) {
        this.parent = parent;
        this.this_parent = this_parent;
        let obj = this;
        this.run = 0;

        this.g = this.parent.append("g")
            .attr("class", "legend");

        /*
        this.rect = this.g.append("rect");
        this.info_time = this.g.append("text")
            .attr("id", "info_time");
        this.info_meteo = this.g.append("text")
            .attr("id", "info_meteo");

        this.padding = 10;
        */

        this.x = x;
        this.y = y;
        this.size = 20;
        this.updateSpeed = 0;

    }

    set data(data) {
        this.data_legend = data;

        this.items = this.g.selectAll('.item').data(this.data_legend);
        this._exit();
        this._enter();
        this.items = this.g.selectAll('.item');
        this._update();
    }

    _exit(){
        this.items.exit().remove();
    }

    _enter(){
         let new_items = this.items.enter().append('g').attr('class', 'item');
         new_items.append('rect')
             .attr('x', 0).attr('width', this.size)
             .attr('y', -this.size/2).attr('height', this.size);
         new_items.append('text')
             .style('alignment-baseline','central')
             .style('text-align', 'right')
             .attr('x', this.size+10);
    }

    _update(){
        let obj = this;

        this.items.select('rect')
            .style('fill', function(d) { return d.colors })
            .style("opacity", .9);
        this.items.select('text')
            .text(function (d) { return d.levels.toString() + obj.this_parent.meteo_data.info.unit })
            .style("color", "black");

        /*
        let allWidths = Array.from(d3.select(".legend").selectAll(".item")._groups[0]).map(function(g){return g.getBBox().width});
        let maxwidth_clients = d3.max(allWidths);
        let space = 20;
        obj.dx = maxwidth_clients + space;
        */
        this.items.attr("transform", function (d, i) {
            return "translate(" + obj.x + "," + (obj.y + obj.size*i) + ")"
        });
    }
}