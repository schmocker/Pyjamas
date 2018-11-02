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

        // Projection
        this.projection = d3.geoMercator()
            .center([11, 47.5])
            .translate([this.width/2, this.height/2])
            .scale([this.width/0.85]);

        this.geo_path = d3.geoPath().projection(this.projection);

        // Country
        this.country = new Country(this.svg, this.geo_path)

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
            this.data_pp = data_pp.result.kw_park;
        }
    }

    async updateView(updateSpeed){
        if (this.data_country){
            this.country.data = this.data_country;
        }
    }

}