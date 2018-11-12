class Country {
    constructor(parent, geo_path) {
        this.parent = parent;
        this.geo_path = geo_path;
        let obj = this;
        this.run = 0;

        this.UCTE_ISO3 =  ["BEL","BIH","BGR","DNK","DEU","FRA","GRC","ITA","HRV","LUX","FYR","MNE","NLD","AUT","POL","PRT","ROU","CHE","SCG","SVK","SVN","ESP","CZE","HUN","MKD","SRB","XKX"];

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
            });
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
