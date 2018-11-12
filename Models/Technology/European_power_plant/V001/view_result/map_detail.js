class Map {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.run = 0;


        // Margin
        this.margin = {top: 50, right: 50, bottom: 50, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;
        /*let w = parseInt($("#map").width());
        let h = parseInt($("#map").height());*/

        // Elements
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .call(d3.zoom().scaleExtent([0.1, 8])
                .on("zoom", function(){
                    let t = d3.event.transform;
                    d3.select(this).select("#countries").attr("transform", t);
                    //d3.select(this).select("#pp").attr("transform", t);
                    //d3.select(this).select("#pp").selectAll('*').attr("r", 4/t.k);
                    //d3.select(this).select("#pp").selectAll('*').style("stroke-width", 1/t.k);
                })
            )
            .on("dblclick.zoom", null);
        //this.zoom = new Zoom(this.svg);

        this.country = new Countries(this.svg, this.width, this.height);
        this.powerplant = new Powerplants(this.svg);


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

        let r=1;
    }

    async updateView(updateSpeed){
        if (this.data_country){
            this.country.data = this.data_country;
        }

        if (this.data_pp){
            this.powerplant.data = this.data_pp;
        }
    }


}

/*
class Zoom {
    constructor(parent) {
        parent.call(d3.zoom().scaleExtent([0.1, 8])
            .on("zoom", function(){
                let t = d3.event.transform;
                d3.select(this).select("#countries").attr("transform", t);
                d3.select(this).select("#pp").attr("transform", t);
                d3.select(this).select("#pp").selectAll('*').attr("r", 4/t.k);
                d3.select(this).select("#pp").selectAll('*').style("stroke-width", 1/t.k);
            })
        )
            .on("dblclick.zoom", null);
    }
}
*/


class Countries {
    constructor(parent, width, height) {
        this.parent = parent;
        this.g = parent.append('g')
            .attr('id', 'countries');

        let projection = d3.geoMercator()
            .center([11, 47.5])
            .translate([width/2, height/2])
            .scale([width/0.85]);

        this.path = d3.geoPath().projection(projection);

        this.UCTE_ISO3 =  ["BEL","BIH","BGR","DNK","DEU","FRA","GRC","ITA","HRV","LUX","FYR","MNE","NLD","AUT","POL","PRT","ROU","CHE","SCG","SVK","SVN","ESP","CZE","HUN","MKD","SRB","XKX"];

        this.tooltip = new ToolTip(parent);
    }

    set data(data) {
        this.items = this.parent.selectAll('.country').data(data.features);
        this._exit();
        this._enter();
        this.items = this.parent.selectAll('.country');
        this._update();
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let obj = this;
        //let new_items = this.items.enter().append("g").attr("class", "country");
        let new_items = this.items.enter();
        new_items.append("path")
            .attr("d", this.path)
            .attr("class", function(d) {
                let classes = "country";
                classes += " " + d.properties.continent;
                classes += (obj.UCTE_ISO3.includes(d.properties.iso_a3)) ? " UCTE" : "";
                return classes;
            })
            .on('mouseover', function(d) {
//                d3.select("#name").html(d.properties.name);
                obj.tooltip.show(d.properties.name);
            })
            .on('mouseout', function() {
//                d3.select("#name").html("");
                obj.tooltip.hide();
            })
            .on('click', function(d) {
                if (obj.UCTE_ISO3.includes(d.properties.iso_a3)){
                    console.log(d.properties.name + " is a UCTE country");
                } else {
                    console.log(d.properties.name + " is not a UCTE country");
                }
            });
    }

    _update() {
        let obj = this;


        // ?????????
        /*
        d3.selectAll(".item").each(function(d, i) {
            d3.select(this).moveToFront();
        });
        */
    }
}

class ToolTip{
    constructor(map){
        this.map = map;

        this.g = this.map.append("g")
            .attr("class", "tooltip")
            .style("opacity", 0);

        this.rect = this.g.append("rect");

        this.value = this.g.append("text").attr("id", "value");

        this.padding = 10;
    }

    show(value){
        this.g.moveToFront();

        let size = parseInt(this.g.style("font-size"));
        this.value.text(value)
            .attr("y",size);

        let height = 2*size; //2.5*size;
        let width = this.value.node().clientWidth;

        this.rect
            .attr("x",-this.padding)
            .attr("y",-this.padding)
            .attr("width", width+2*this.padding)
            .attr("height", height+2*this.padding);

        this.g
            .attr("transform", "translate(" + (40) + "," + (40) + ")")
            .transition().duration(this.updateSpeed)
            .style("opacity", .9);
//            .attr("transform", "translate(" + (this.axis.xScale(xVal)-width/2) + "," + (this.axis.yScale(yVal)-10-this.padding-height) + ")")
    }

    hide(){
        this.g.transition()
            .duration(this.updateSpeed)
            .style("opacity", 0);
    }
}


class Powerplants {
    constructor(parent) {
        this.parent = parent;
        let obj = this;

        this.pp_groupe = this.parent.append('g')
            .attr('id', 'pp');

        this.pp_items = null;
        this.tooltip_pp = new ToolTip_PP(parent);

    }
    set data(data){
        this.pp_items = this.parent.selectAll('.circle').data(data);
        this._exit();
        this._enter();
        this.pp_items = this.parent.selectAll('.circle');
        this._update();
    }

    _exit(){
        this.pp_items.exit().remove();
    }

    _enter(){
        let new_pp_items = this.pp_items.enter();
        new_pp_items.append("g").attr("class", "circles");
    }

    _update(){
        let obj = this;

        // Circles
        //let data_circles = [{x: 47, y: 8}, {x: 40, y: 30}];
        let data_circles = this.pp_items.lat.map(function (d, id_d) {
            return {lon: obj.lon[id_d], lat: obj.lat[id_d]};
        });
        let circles = this.pp_items.select(".circles").selectAll("circle")
            .data(data_circles);


        circles.exit().remove();

        circles.enter().append('circle')
            .attr("r", 3).style("opacity", 0)
            .on("mouseover", function(d) { obj.tooltip_pp.show(d.lon, d.lat, obj.pp_items.kw_bezeichnung); })
            .on("mouseout", function() { obj.tooltip_pp.hide(); });

        circles = this.pp_items.select(".circles").selectAll("circle");

        circles
            .style("stroke", "blue")
            .style("fill", "blue")
            .attr("cx", function(d) { return projection(d.lon); })
            .attr("cy", function(d) { return projection(d.lat); });
        /*
        circles
            .style("stroke", function() {return obj.axis.zScale(this.parentNode.__data__.id); })
            .style("fill", function() {return obj.axis.zScale(this.parentNode.__data__.id); });
        circles
            .transition().duration(this.updateSpeed)
            .attr("cx", function(d) { return obj.axis.xScale(d.date); })
            .attr("cy", function(d) { return obj.axis.yScale(d.y); });
        circles
            .transition().delay(this.updateSpeed)
            .style("opacity", 1);
        */
    }
}


class ToolTip_PP{
    constructor(powerplant){
        this.powerplant = powerplant;
        this.updateSpeed = 200;

        this.g = this.powerplant.append("g")
            .attr("class", "tooltip")
            .style("opacity", 0);

        this.rect = this.g.append("rect");

        this.xVal = this.g.append("text").attr("id", "xVal");
        this.yVal = this.g.append("text").attr("id", "yVal");
        this.name = this.g.append("text").attr("id", "Name");

        this.padding = 10;
    }

    show(xVal, yVal, name){

        this.g.moveToFront();

        let size = parseInt(this.g.style("font-size"));
        this.xVal.text(xVal)
            .attr("y",size);
        this.yVal.text(yVal)
            .attr("y",2.5*size);
        this.name.text(name)
            .attr("y",5*size);

        let height = 5*size; //2.5*size;

        let wx = this.xVal.node().clientWidth;
        let wy = this.yVal.node().clientWidth;
        let wn = this.name.node().clientWidth;
        let width = Math.max(wx,wy,wn);

        this.rect
            .attr("x",-this.padding)
            .attr("y",-this.padding)
            .attr("width", width+2*this.padding)
            .attr("height", height+2*this.padding);

        this.g
            .attr("transform", "translate(" + (this.powerplant.xScale(xVal)-width/2) + "," + (this.powerplant.yScale(yVal)-10-this.padding-height) + ")")
            .transition().duration(this.updateSpeed)
            .style("opacity", .9);
    }

    hide(){
        this.g.transition()
            .duration(this.updateSpeed)
            .style("opacity", 0);
    }
}

