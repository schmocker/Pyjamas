let UCTE_ISO3 =  ["BEL","BIH","BGR","DNK","DEU","FRA","GRC","ITA","HRV","LUX","FYR","MNE","NLD","AUT","POL","PRT","ROU","CHE","SCG","SVK","SVN","ESP","CZE","HUN","MKD","SRB","XKX"];



let settings;
let powerplants;






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



let json
let projection;

window.onload = async function(){



    let w = parseInt($("#map").width());
    let h = parseInt($("#map").height());

    //Define map projection
    projection = d3.geoMercator() //utiliser une projection standard pour aplatir les pôles, voir D3 projection plugin
        .center([ 11, 47.5 ]) //comment centrer la carte, longitude, latitude
        .translate([ w/2, h/2 ]) // centrer l'image obtenue dans le svg
        .scale([ w/0.85 ]); // zoom, plus la valeur est petit plus le zoom est gros

//Define path generator
    let path = d3.geoPath().projection(projection);


    //Create SVG
    let svg = d3.select("#map")
        .append("svg")
        .attr("width", w)
        .attr("height", h)
        .call(d3.zoom().scaleExtent([0.1, 8])
            .on("zoom", function(d){
                let t = d3.event.transform;
                d3.select(this).select("#countries").attr("transform", t);
                d3.select(this).select("#pp").attr("transform", t);
                d3.select(this).select("#pp").selectAll('*').attr("r", 4/t.k);
                d3.select(this).select("#pp").selectAll('*').style("stroke-width", 1/t.k);
            })
        )
        .on("dblclick.zoom", null);
//Load in GeoJSON data
    json = await d3.json(data_url)

    //Bind data and create one path per GeoJSON feature
    let countries = svg.append('g').attr('id','countries');

    countries.selectAll(".country")
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
    });

    powerplants = new Powerplants(svg);


    settings = new Settings();


    await powerplants.build();
    await settings.build();




};

async function update() {
    
}



function log(x) {
    console.log(x);
}

async function post(fnc_str, data_dict){
    let data = await $.post("/websimgui", {
        'fnc': fnc_str,
        'data': JSON.stringify(data_dict)
    });
    data = JSON.parse(data);
    if (data === "false"){
        alert('POST request returned "false", check the request for the function "' + fnc_str + '"!');
        return false
    } else {
        return data;
    }
}

async function get(fnc_str, data_dict){
    let data = await $.get("/websimgui", {
        'fnc': fnc_str,
        'data': JSON.stringify(data_dict)});
    if (data === "false"){
        alert('GET request returned "false", check the request for the function "' + fnc_str + '"!');
        return false
    } else {
        return data;
    }
}




















