class Box {
    constructor(WebSimGui, id, model_obj) {
        this.WebSimGui = WebSimGui;
        this.id = id;

        let this_box = this;
        this.div = d3.select("#working_field").append('div')
            .html('<div class="name">'+model_obj.name+'</div>')
            .classed("box", true)
            .call(d3.drag()
                .on("start", function() {this_box.on_dragstart(d3.event)})
                .on("drag", function() {this_box.on_drag(d3.event)})
                .on("end", function() {this_box.on_dragend(d3.event)}))
            .on("mouseover", function() {this_box.on_hover(d3.event)})
            .on("dblclick ", function() {this_box.on_dbclick(d3.event)});

        this.pos = d3.range(2).map(function() {
            return {
                x: model_obj.posX,
                y: model_obj.posY,
                width: model_obj.width,
                height: model_obj.height
            };
        });

        this.model = websimgui.svgContainer.append("g")
            .classed("model",true)
            .data(this.pos)
            .enter()

        this.box = this.model.append("rect")
            .classed("box",true)
            .attr("x", function(d) { return d.x; })
            .attr("y", function(d) { return d.y; })
            .attr("width", function(d) { return d.width; })
            .attr("height", function(d) { return d.height/2; })
            .call(d3.drag()
                .on("start", function (d) {})
                .on("drag", function (d) {
                    let model = d3.select(d3.select(this).node().parentNode);
                    update_box_pos(model,d,d3.event.x,d3.event.y);
                })
                .on("end", function (d) {})
            );



        this.box_sizer = this.model.append("rect")
            .classed("box_sizer",true)
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", 10)
            .attr("height", 10)
            .call(d3.drag()
                .on("start", function (d) {})
                .on("drag", function (d) {
                    let model = d3.select(d3.select(this).node().parentNode);
                    let width = parseFloat(model.select(".box").attr("width")) + d3.event.dx;
                    let height = parseFloat(model.select(".box").attr("height")) + d3.event.dy;
                    update_box_size(model,d,width,height);
                })
                .on("end", function (d) {})
            );

        this.box_name = this.model.append("text")
            .classed("box_name",true)
            .attr("x", function(d) { return d.x; })
            .attr("y", function(d) { return d.y; })
            .attr("text-anchor", "middle")
            .text(model_obj.name)
            .call(d3.drag()
                .on("start", function (d) {})
                .on("drag", function (d) {
                    let model = d3.select(d3.select(this).node().parentNode);
                    update_box_pos(model,d,d3.event.x,d3.event.y);
                })
                .on("end", function (d) {})
            );

        this.input = this.model.append("g")
            .classed("input",true);

        this.output = this.model.append("g")
            .classed("output",true);

        //this.input = new Rail(this, 'in', 'left', model_obj.inputs);
        //this.output = new Rail(this, 'out', 'right', model_obj.outputs);



        function update_box_size(model,d,width, height){
            model.select(".box")
                .attr("width", d.width = Math.max(width,30))
                .attr("height", d.height = Math.max(height,30));
            update_box_name_pos(model);
            update_box_sizer_pos(model);
        }

        function update_box_pos(model,d,x,y){
            model.select(".box").attr("x", d.x = x).attr("y", d.y = y);
            update_box_name_pos(model);
            update_box_sizer_pos(model);
        }

        function update_box_name_pos(model){
            let box = model.select(".box");
            let box_name = model.select(".box_name");
            box_name
                .attr("x", parseFloat(box.attr("x")) + box.attr("width")/2)
                .attr("y", parseFloat(box.attr("y")) + box.attr("height")/2 + parseFloat(box_name.style("font-size"))/2);
        }

        function update_box_sizer_pos(model){
            let box = model.select(".box");
            let box_sizer = model.select(".box_sizer");
            box_sizer
                .attr("x", parseFloat(box.attr("x")) + parseFloat(box.attr("width"))-parseFloat(box_sizer.attr("width")))
                .attr("y", parseFloat(box.attr("y")) + parseFloat(box.attr("height"))-parseFloat(box_sizer.attr("height")));
        }

        function update_rail_pos(model){

        }

    }

    get position() {
        var abs_pos = this.div.node().getBoundingClientRect();

        var pos = {};
        pos["width"] = abs_pos["width"];
        pos["height"] = abs_pos["height"];

        pos["left"] = parseFloat(this.div.style("left"));
        pos["x1"] = pos["left"];
        pos["right"] = pos["left"] + pos["width"];
        pos["x2"] = pos["right"];

        pos["top"] = parseFloat(this.div.style("top"));
        pos["y1"] = pos["top"];
        pos["bottom"] = pos["top"] + pos["height"];
        pos["y2"] = pos["bottom"];

        pos["x_center"] = pos["x1"] + pos["width"] / 2;
        pos["y_center"] = pos["y1"] + pos["height"] / 2;
        return pos
    }

    on_dbclick() {
        alert("Settings not yet implemented");
    }

    on_hover() {
        $(".box").css("z-index", "0");
        $(this).css("z-index", "1");
    }
    on_dragstart(evt) {
        this.div.classed("box_drag", true);
    }
    on_drag(evt) {
        this.div.classed("box_drag", true);
        var x = parseFloat(this.div.style("left")) + evt.dx;
        var y = parseFloat(this.div.style("top")) + evt.dy;
        this.updatePosition(x,y);
    }

    on_dragend(evt) {
        this.updatePosition();
        this.div.classed("box_drag", false);
        let data = {
            'box': this.id,
            'position': this.position
        };
        $.post('/websimgui', {
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: 'POST'
        }, function (data) {
            console.log(data);
        });
    }

    updatePosition(x,y){
        //eigene Position
        this.div.style("left", x + "px");
        this.div.style("top", y + "px");
    }


}