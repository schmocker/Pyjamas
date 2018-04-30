class Port{
    constructor(rail,id,port_obj) {
        this.rail = rail;
        this.pos = [0,0];

        this.id = id;

        this.connections = {};

        this.size = 10;
        let thisPort = this;
        let line;
        this.triangle = websimgui.svgContainer.append("polyline")
            .classed("port", true)
            .attr("model", this.rail.model.id)
            .attr("direction", this.rail.direction)
            .attr("id", id)
            .attr("points", "0,0")//.on("mousedown", function(){thisPort.connecting(d3.event)})
            .call(d3.drag()
                .on("start", function (d) {
                    line = websimgui.svgContainer.append("line")
                        .style("stroke", "black")
                        .style("stroke-dasharray", "5,5")
                        .attr("x1", thisPort.linePoint[0])
                        .attr("y1", thisPort.linePoint[1])
                        .attr("x2", thisPort.linePoint[0])
                        .attr("y2", thisPort.linePoint[1]);
                })
                .on("drag", function (d) {
                    var pos = d3.mouse(this);
                    line.attr("x2", pos[0]);
                    line.attr("y2", pos[1]);
                })
                .on("end", function (d) {

                })
            );

        //.on("mouseover", function(){d3.select(this).attr("fill", "blue")})
        //.on("mouseout", function(){d3.select(this).attr("fill", "black")});
    }

    get linePoint(){
        switch (this.rail.orientation){
            case "left":
                return [this.pos[0]-this.size, this.pos[1]];
            case "right":
                return [this.pos[0]+this.size, this.pos[1]];
        }
    }

    connecting(evt){
        let triangle1 = this.triangle;
        var line = websimgui.svgContainer.append("line")
            .style("stroke", "black")
            .style("stroke-dasharray", "5,5")
            .attr("x1", this.linePoint[0])
            .attr("y1", this.linePoint[1])
            .attr("x2", this.linePoint[0])
            .attr("y2", this.linePoint[1]);

        let in_out;
        switch (this.rail.direction){
            case "in":
                in_out = "out";
                break;
            case "out":
                in_out = "in";
                break;
        }
        console.log(in_out);


        this.triangle
            .classed("port_choice1", true)
            .classed("port", false);

        d3.selectAll('.port')
            .classed("port_inselectable", true)
            .classed("port", false);

        d3.selectAll('.port_inselectable')
            .filter(function(d, i) {return d3.select(this).attr("direction") === in_out;})
            .filter(function(d, i) {return d3.select(this).attr("model") !== triangle1.attr("model");})
            .classed("port_inselectable", false)
            .classed("port_selectable", true);

        ////
        let selection;
        d3.selectAll('.port_selectable')
            .on("mouseover", function() {
                selection = this;
                var sel = d3.select(this);
                sel.moveToFront();
                //sel.classed("port_choice2", true);
            })
            .on("mouseout", function(d, i) {
                selection = null;
                var sel = d3.select(this);
                //sel.classed("port_choice2", false);
            });




        var w = websimgui.svgContainer
            .on("mousemove", function(){
                var pos = d3.mouse(this);
                line.attr("x2", pos[0]);
                line.attr("y2", pos[1]);
                let sel = d3.select(".port_selection");
                //sel.parentNode.appendChild(sel);
            })
            .on("mouseup", mouseup);

        d3.event.preventDefault();

        function mouseup() {
            console.log(selection);
            line.remove();
            w.on("mousemove", null).on("mouseup", null);

            d3.selectAll('.port_choice1').classed("port_choice1", false).classed("port", true);
            d3.selectAll('.port_inselectable').classed("port_inselectable", false).classed("port", true);
            d3.selectAll('.port_selectable').classed("port_selectable", false).classed("port", true);

            let fromModelID = triangle1.attr("model");
            let fromPortID = triangle1.attr("id");
            let fromPort = websimgui.boxes[fromModelID].output.ports[fromPortID];


            let toModelID = d3.select(selection).attr("model");
            let toPortID = d3.select(selection).attr("id");
            let toPort = websimgui.boxes[toModelID].input.ports[toPortID];


            let r = new Connection(fromPort, toPort, websimgui.svgContainer);
            r.updatePosition();
        }

    }

    updatePosition(x,y){
        this.pos = [x,y];

        let form;
        switch (this.rail.orientation + "|" + this.rail.direction){
            case "left|in":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break;
            case "left|out":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break; // unused for now
            case "right|in":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break; // unused for now
            case "right|out":
                form = [0,this.size/1.5,this.size,0,0,-this.size/1.5]; break;
            case "top|in":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break; // unused for now
            case "top|out":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break; // unused for now
            case "bottom|in":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break; // unused for now
            case "bottom|out":
                form = [-this.size,this.size/1.5,0,0,-this.size,-this.size/1.5]; break; // unused for now
        }


        var point = "X1,Y1 X2,Y2 X3,Y3"
            .replace("X1",form[0]+x)
            .replace("Y1",form[1]+y)
            .replace("X2",form[2]+x)
            .replace("Y2",form[3]+y)
            .replace("X3",form[4]+x)
            .replace("Y3",form[5]+y);

        this.triangle.attr("points", point);

        for (let connection_id in this.connections){
            this.connections[connection_id].updatePosition();
        }
    }
}
