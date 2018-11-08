class Meteo {
    constructor(parent, projection) {
        this.parent = parent;
        this.projection = projection;
        let obj = this;
        this.run = 0;

        this.meteo_g = this.parent.g.append('g')
            .attr('id', 'meteos')

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

        // projection
        let coord_topleft = obj.projection([d3.min(this.meteo_data.lon), d3.max(this.meteo_data.lat)])
        let coord_topright = obj.projection([d3.max(this.meteo_data.lon), d3.max(this.meteo_data.lat)])
        let coord_bottomleft = obj.projection([d3.min(this.meteo_data.lon), d3.min(this.meteo_data.lat)])
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


        // colors etc
        let min_value = d3.min(this.meteo_data.values);
        let max_value = d3.max(this.meteo_data.values);
        let delta_value = max_value - min_value;


        let color = d3.scaleSequential(d3.interpolateRdBu);

        // contour
        //let i0 = d3.interpolateHsvLong(d3.hsv(120, 1, 0.65), d3.hsv(60, 1, 0.90));
        //let i1 = d3.interpolateHsvLong(d3.hsv(60, 1, 0.90), d3.hsv(0, 0, 0.95));
        //let interpolateTerrain = function(t) { return t < 0.5 ? i0(t * 2) : i1((t - 0.5) * 2); };
        //let color = d3.scaleSequential(interpolateTerrain).domain([0, 100]);

        let new_items = this.items.enter();
        new_items.append("path")
//            .attr("d", d3.geoPath(d3.geoIdentity().fitExtent([coord_topleft, [coord_width, coord_height]], new_items)))
//            .attr("d", d3.geoPath(d3.geoIdentity().scale(coord_width / obj.meteo_data.width)))
            .attr("d", d3.geoPath().projection(scale(scale_x, scale_y)))
            .attr("fill", function(d) { return color(-d.value*0.017+0.5); }) // 50: 0.01, 30: 0.016667
            .attr("transform", "translate(" + coord_topleft[0].toString() + "," + coord_topleft[1].toString() + ")")
            .style("opacity", 0.1);
    }

    _update() {
        let obj = this;

    }

}
