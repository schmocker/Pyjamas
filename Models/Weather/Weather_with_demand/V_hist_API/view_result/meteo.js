class Meteo {
    constructor(parent, projection) {
        this.parent = parent;
        this.projection = projection;
        let obj = this;
        this.run = 0;

        this.meteo_g = this.parent.g.append('g')
            .attr('id', 'meteos')

        this.information = new Information(this.parent.g);

    }

    set data(data) {
        this.meteo_data = data;
        this.items = this.meteo_g.selectAll('.meteo').data(
            d3.contours()
                .size([this.meteo_data.width, this.meteo_data.height])
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
            .style("opacity", 0.1);

        this.information.show(this.meteo_data.info.info_time, this.meteo_data.info.info_meteo)
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