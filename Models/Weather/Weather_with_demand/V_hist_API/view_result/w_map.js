class W_map {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.run = 0;
        this.TimeType_ID = 0;

        // Margin
        this.margin = {top: 50, right: 50, bottom: 50, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // Elements
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom);

        this.g = this.svg.append("g");

        // Projection
        this.projection = d3.geoMercator()
            .center([11, 48.5])     //.center([11, 47.5])
            .translate([this.width/2, this.height/2])
            .scale([this.width/0.85]);

        this.geo_path = d3.geoPath().projection(this.projection);

        // Country
        this.country = new Country(this, this.geo_path);

        // Power plant
        this.meteo = new Meteo(this, this.projection);

    }

    async setMeteoType(id) {
        this.MeteoType_ID = id;
        this.run = 0;
        await this.updateData();
        await this.updateView();
    }

    async setTimeType(id) {
        let change = this.TimeType_ID !== id;
        this.TimeType_ID = id;
        if(change){
            this.run = 0;
            await this.updateData();
            await this.updateView();
        }
    }

    async updateData() {
        let obj = this;

        // data of country
        let data_country = await d3.json(data_url);
        if (data_country) {
            this.data_country = data_country;
        }

        // select meteo type
        let i_meteotype = -1;
        let i_meteotype_s;
        let col_scale_range;
        let col_scale_prop;
        let col_scheme;
        let threshold;
        let unit;

        switch (obj.MeteoType_ID) {

            case "Temperature":
                i_meteotype = 1;
                i_meteotype_s = "temperature";
                col_scale_range = [-40, 40];  // inverse RedBlu // [-50, 50];
                col_scale_prop = [-1/(col_scale_range[1]-col_scale_range[0]),
                col_scale_range[1]/(col_scale_range[1]-col_scale_range[0])];
                threshold = 15;
                //threshold = d3.range(col_scale_range[0], col_scale_range[1]+1,
                //    (col_scale_range[1]-col_scale_range[0])/40);
                col_scheme = d3.interpolateRdBu;
                unit = " °C";
                break;
            case "Wind speed":
                i_meteotype = 2;
                i_meteotype_s = "windspeed";
                col_scale_range = [0, 20];
                col_scale_prop = [1/(col_scale_range[1]-col_scale_range[0]),
                -col_scale_range[0]/(col_scale_range[1]-col_scale_range[0])];
                threshold = 10;
                col_scheme = d3.interpolateBlues;
                unit = " m/s";
                break;
            case "Radiation":
                i_meteotype = 3;
                i_meteotype_s = "radiation";
                col_scale_range = [0, 1000];
                col_scale_prop = [1/(col_scale_range[1]-col_scale_range[0]),
                -col_scale_range[0]/(col_scale_range[1]-col_scale_range[0])];
                threshold = 10;
                col_scheme = d3.interpolateReds;
                unit = " W/m^2 K";
                break;
            default:
                break;
        }

        // select time type
        let i_timetype = 0;
        /*
        let fut_formatted = data_meteo.futures.map(function (c) {return new Date(c*1E3)});
        fut_formatted = fut_formatted.map(function (c) {return c.timeformat()});
        if (data_meteo) {
            i_timetype = fut_formatted.findIndex(function (i) {
                return i === obj.TimeType_ID;
            });
        }
        */
        i_timetype = this.TimeType_ID; // take always current state


        // data of meteo
        let filter = {'data': ['Map_weather',i_timetype,i_meteotype_s],
                      'coord': ['Map_weather','coord'],
                      'futures': ['Map_weather','futures']};
        let data_dict_meteo = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data_meteo = await get(data_dict_meteo);
        data_meteo = JSON.parse(data_meteo);
        data_meteo = data_meteo.result;

        // data
        if (data_meteo && i_meteotype >= 0 && i_timetype >= 0) {
            let data_temp = data_meteo["data"];
            let vec_lat = data_meteo["coord"]["lat"];
            let vec_lon = data_meteo["coord"]["lon"];
            let info_time = new Date(data_meteo.futures[i_timetype]*1E3);
            info_time = info_time.timeformat();

            let data_filter = {
                "lat": vec_lat,
                "lon": vec_lon,
                "width": vec_lon.length,
                "height": vec_lat.length,
                "values": data_temp,
                "scale": {"col_scale_prop": col_scale_prop,
                    "threshold": threshold,
                    "col_scheme": col_scheme},
                "info": {"info_time": info_time,
                    "info_meteo": obj.MeteoType_ID,
                    "unit": unit}
            };

            //
            this.data_meteo = data_filter;
        }
    }

    async updateView(updateSpeed){
        if (this.data_country){
            this.country.data = this.data_country;
            if (this.data_meteo){
                this.meteo.data = this.data_meteo;
            }
        }
    }

}