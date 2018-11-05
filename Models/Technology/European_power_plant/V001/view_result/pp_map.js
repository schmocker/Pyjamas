class PP_Map {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.run = 0;

        // Margin
        this.margin = {top: 50, right: 50, bottom: 50, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // Elements
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)

        this.g = this.svg.append("g");

        // Projection
        this.projection = d3.geoMercator()
            .center([11, 47.5])
            .translate([this.width/2, this.height/2])
            .scale([this.width/0.85]);

        this.geo_path = d3.geoPath().projection(this.projection);

        // Country
        this.country = new Country(this, this.geo_path);

        // Power plant
        this.powerplant = new Powerplant(this, this.projection);

        // Zoom
        this.zoom = new Zoom(this);


    }

    async updateData() {
        let obj = this;

        // data of country
        let data_country = await d3.json(data_url);
        if (data_country) {
            this.data_country = data_country;
        }

        // data of power plants
        let filter = {};
        let data_dict_pp = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data_pp = await get(data_dict_pp);
        data_pp = JSON.parse(data_pp);
        if (data_pp) {
            let data_temp = data_pp.result.kw_park;

            // restructure
            let data_key = Object.keys(data_temp);
            let data_id = data_temp["id"];
            let data_temp_2 = [];
            this.data_pp = data_id.map(function (c, id_c) {
                return {
                    id: data_temp["id"][id_c],
                    kw_bezeichnung: data_temp["kw_bezeichnung"][id_c],
                    lat: data_temp["lat"][id_c],
                    long: data_temp["long"][id_c]
                }
            })
        }
    }

    async updateView(updateSpeed){
        if (this.data_country){
            this.country.data = this.data_country;
            if (this.data_pp){
                this.powerplant.data = this.data_pp;
            }
        }
    }

}

class Zoom {
    constructor(parent) {
        this.parent = parent;
        let obj = parent;

        let g = this.parent.g;
        g.call(d3.zoom().scaleExtent([0.1, 8])
            .on("zoom", function(){
                let t = d3.event.transform;
                d3.select(this).selectAll("g").selectAll("path").attr("transform", t);
                d3.select(this).selectAll("g").selectAll("circle")
                    .attr("transform", t)
                    .attr("r", 4/t.k);
            })
        )


    }
}