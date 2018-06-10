class Powerplants {
    constructor(parent) {
        this.parent = parent;
        let obj = this;
        this.data = null;

        this.pp_groupe = this.parent.append('g').attr('id','pp');
        this.active = null;


    }

    async build(){
        let obj = this;
        let Props_json = await get('get_model_properties', {'model': mu_id});
        this.data = JSON.parse(Props_json).powerplant;


        this.pp_groupe.selectAll("circle").remove();

        this.pp_groupe.selectAll("circle")
            .data(this.data).enter()
            .append("circle")
            .attr("class","item")
            .attr("cx", function (d) { return projection(d.lonlat)[0]; })
            .attr("cy", function (d) { return projection(d.lonlat)[1]; })
            .attr("r", "4px")
            .on('mouseover', function(d) {
                d3.select("#name").html(d.name);
            })
            .on('mouseout', function(d) {
                d3.select("#name").html("");
            })
            .call(d3.drag()
                .on("start", await async function (d) {
                    await obj.activate(d3.select(this))
                })
                .on("drag", await async function (d) {
                    let lonlat = projection(d.lonlat);
                    lonlat[0] += d3.event.dx;
                    lonlat[1] += d3.event.dy;
                    d.lonlat = projection.invert(lonlat);
                    await obj.update();

                    await settings.update();

                })
                .on("end", await async function (d) {
                    await obj.sendPP();
                }))

        await this.update();
    }

    async update(){
        this.pp_groupe.selectAll("circle")
            .attr("cx", function (d) { return projection(d.lonlat)[0]; })
            .attr("cy", function (d) { return projection(d.lonlat)[1]; })
    }

    async addPP(){
        let latlon = projection.center();
        this.data.push({'name': 'Windturbine', 'lonlat': latlon});
        await this.sendPP();
        await this.build();
    }

    async sendPP(){
        let data = await post('set_model_property', {'model': mu_id, 'property': 'powerplant', 'value': this.data});
        log(data);
    }

    async activate(pp){
        this.active = pp;
        this.pp_groupe.selectAll("circle").style('stroke', 'white');
        pp.style('stroke', 'red');
        await settings.update();
    }

    // active PP
    async delete_active(){
        this.index = this.data.indexOf(this.active.data()[0]);
        this.data.splice(this.index, 1);
        await this.sendPP();
        await this.build();
    }

    get name(){ return (this.active !== null) ? this.active.data()[0].name : ""; }
    get lat(){ return (this.active !== null) ? this.active.data()[0].lonlat[0] : ""; }
    get lon(){ return (this.active !== null) ? this.active.data()[0].lonlat[1] : ""; }

    set name(name){
        this.active.data()[0].name = name;
    }
    set lat(lat){
        this.active.data()[0].lonlat[0] = lat;
        this.update();
    }
    set lon(lon){
        this.active.data()[0].lonlat[1] = lon;
        this.update();
    }
}