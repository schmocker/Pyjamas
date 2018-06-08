let UCTE_ISO3 =  ["BEL","BIH","BGR","DNK","DEU","FRA","GRC","ITA","HRV","LUX","FYR","MNE","NLD","AUT","POL","PRT","ROU","CHE","SCG","SVK","SVN","ESP","CZE","HUN","MKD","SRB","XKX"];


let KWP = [];
KWP.push({'Kraftwerkstyp': 'Windturbine', 'lonlat':[0,40]});
KWP.push({'Kraftwerkstyp': 'PV-Anlage', 'lonlat':[13,52]});
KWP.push({'Kraftwerkstyp': 'Gasturbine', 'lonlat':[-13,52]});


//Width and height




d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};
d3.selection.prototype.moveToBack = function() {
    return this.each(function() {
        var firstChild = this.parentNode.firstChild;
        if (firstChild) {
            this.parentNode.insertBefore(this, firstChild);
        }
    });
};


window.onload = function(){
    let w = parseInt($("#map").width());
    let h = parseInt($("#map").height());

    //Define map projection
    let projection = d3.geo.mercator() //utiliser une projection standard pour aplatir les pôles, voir D3 projection plugin
        .center([ 11, 47.5 ]) //comment centrer la carte, longitude, latitude
        .translate([ w/2, h/2 ]) // centrer l'image obtenue dans le svg
        .scale([ w/0.85 ]); // zoom, plus la valeur est petit plus le zoom est gros

//Define path generator
    let path = d3.geo.path()
        .projection(projection);


    //Create SVG
    let svg = d3.select("#map")
        .append("svg")
        .attr("width", w)
        .attr("height", h);
//Load in GeoJSON data
    d3.json(data_url, function(json) {

        //Bind data and create one path per GeoJSON feature
        svg.selectAll(".country")
            .data(json.features).enter()
            .append("path")
            .attr("d", path)
            .attr("class",function(d) {
                let classes = "country";
                classes += " " + d.properties.continent;
                classes += (UCTE_ISO3.includes(d.properties.iso_a3)) ? " UCTE" : "";
                return classes;
            })
            .on('mouseover', function(d) {
                d3.select("#name").html(d.properties.name);
            })
            .on('mouseout', function(d) {
                d3.select("#name").html("");
            })
            .on('click', function(d) {
                if (UCTE_ISO3.includes(d.properties.iso_a3)){
                    console.log(d.properties.name + " is a UCTE country");
                } else {
                    console.log(d.properties.name + " is not a UCTE country");
                }
            });




        d3.selectAll(".item").each(function(d, i) {
            d3.select(this).moveToFront();
        })



    });
    svg.selectAll("circle")
        .data(KWP).enter()
        .append("circle")
        .attr("class","item")
        .attr("cx", function (d) { return projection(d.lonlat)[0]; })
        .attr("cy", function (d) { return projection(d.lonlat)[1]; })
        .attr("r", "4px")
        .on('mouseover', function(d) {
            d3.select("#name").html(d.Kraftwerkstyp);
        })
        .on('mouseout', function(d) {
            d3.select("#name").html("");
        });

};





















