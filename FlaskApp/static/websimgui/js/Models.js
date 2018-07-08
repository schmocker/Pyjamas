class Models {
    constructor() {
        let obj = this;


        this.sizer = {};
        this.sizer.size = 10;

        this.text_offset = {'left': [4,0], "right": [-4,0], "top": [0,4], "bottom": [0,-4]};


        this.array = {};
        this.array.size = 15;
        this.array.forms = {};
        let orientations = ['left','right','top','bottom'];
        let directions = ['input','output'];

        for (let i in orientations){
            let M = {};
            for (let j in directions){
                M[directions[j]] = this.get_port_arrow_form(orientations[i], directions[j], this.array.size);
            }
            this.array.forms[orientations[i]] = M;
        }


    }

    async build() {
        let obj = this;

        let all_models = main.selectAll(".model"); //!!!!!!!
        all_models.remove();

        ////////////////////////////////
        //////////// models ////////////
        ////////////////////////////////
        //join
        let models = main.selectAll(".model").data(d3.values(agent_data.model_used));


        //exit: delete unused models
        models.exit().remove();

        //enter: create new if need
        models = models.enter().append("g")
            .classed("model", true)
            .attr("id", function (d) { return "mu_"+d.id;
            });
        models.append("rect")
            .classed("box", true)
            .on("click", async function (mu) { await obj.activate(mu.id); })
            .call(await obj.onModelDrag());
        models.append("text")
            .classed("model_name", true)
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "top");
        models.append("rect")
            .classed("sizer", true)
            .call(await obj.onModelResize());

        // update models
        models = main.selectAll(".model");

        ///////////////////////////////
        //////////// docks ////////////
        ///////////////////////////////
        //join
        let docks = models.selectAll(".dock").data(function (mu) {
            let m = agent_data.models[mu.fk_model];
            let docks = {};
            docks.inputs = m.inputs;
            docks.outputs = m.outputs;
            return d3.entries(docks);
        });

        //exit
        docks.exit().remove();

        //enter
        docks = docks.enter()
            .append("g")
            .classed("dock", true)
            .attr("id", function (d) {d.key});

        // update
        docks = models.selectAll(".dock");

        ///////////////////////////////
        //////////// ports ////////////
        ///////////////////////////////
        // join
        let ports = docks.selectAll(".port").data(function (m) { return d3.entries(m.value) });

        //exit
        ports.exit().remove();

        //enter
        ports = ports.enter()
            .append("g")
            .classed("port", true)
            .attr("id_model", function (d) {
                return d.id_model
            });
        ports.append("polyline")
            .classed("arrow", true)
            .call(await obj.onConnecting());
        ports.append("text")
            .classed("port_name", true)
            .call(await obj.onPortDrag());



        ////////////////////////////////////
        //////////// update all ////////////
        ////////////////////////////////////
        models = main.selectAll(".model");
        models.each(await async function (d,i){
            let model = d3.select(this);
            let d_model = d;
            model.selectAll(".port").each(await async function (d,i){
                d.model = d_model.id;
                d3.select(this).select(".arrow")
                    .attr("id", function (d) { return d.key })
            })
        });
        await this.update();
    }


    async update() {
        // fast update only positions
        let obj = this;

        let models = main.selectAll(".model");
        models.select(".box")
            .attr("x", function(d){ return d.x })
            .attr("y", function(d){ return d.y })
            .attr("width", function(d){ return d.width })
            .attr("height", function(d){ return d.height });
        models.select(".model_name")
            .text( function(d){ return d.name })
            .attr("x", function(d){
                switch (d.name_h_position){
                    case 'left outside': return d.x - 4;
                    case 'left inside': return d.x + 4;
                    case 'center': return d.x + d.width / 2;
                    case 'right inside': return d.x + d.width - 4;
                    case 'right outside': return d.x + d.width + 4;
                    default: return d.x + d.width / 2;
                }})
            .attr("text-anchor", function (d) {
                switch (d.name_h_position){
                    case 'left outside': return 'end';
                    case 'left inside': return 'start';
                    case 'center': return 'middle';
                    case 'right inside': return 'end';
                    case 'right outside': return 'start';
                    default: return 'middle';
                }})
            .attr("y", function(d){
                switch (d.name_v_position){
                    case 'top outside': return d.y - 4;
                    case 'top inside': return d.y + 4;
                    case 'center': return d.y + d.height/2;
                    case 'bottom inside': return d.y + d.height - 4;
                    case 'bottom outside': return d.y + d.height + 4;
                    default: return d.y - 4;
                }})
            .attr("alignment-baseline", function (d) {
                switch (d.name_v_position){
                    case 'top outside': return 'baseline';
                    case 'top inside': return 'hanging';
                    case 'center': return 'middle';
                    case 'bottom inside': return 'baseline';
                    case 'bottom outside': return 'hanging';
                    default: return 'baseline';
                }});
        models.select(".sizer")
            .attr("x", function(d){ return d.x + d.width - obj.sizer.size / 2 })
            .attr("y", function(d){ return d.y + d.height - obj.sizer.size / 2 })
            .attr("width", function(d){ return obj.sizer.size })
            .attr("height", function(d){ return obj.sizer.size });

        models.each(await async function (d,i){ // for each model
            let model = d3.select(this);
            let d_model = d;
            let docks = model.selectAll(".dock");

            docks.each(await async function (d,i){ // for each dock in this model
                d.direction = d.key.substring(0, d.key.length - 1);
                d.orientation = d_model[d.direction+'_orientation'];
                d.numOfPorts = Object.keys(d.value).length;

                let dock = d3.select(this);
                let d_dock = d;

                let ports = dock.selectAll(".port");

                let form = obj.array.forms[d_dock.orientation][d_dock.direction];


                let x0 = d_model.x;
                let y0 = d_model.y;
                let dx;
                let dy;
                switch (d_dock.orientation) {
                    case "left":
                    case "right":
                        dx = 0;
                        dy = d_model.height / d_dock.numOfPorts;
                        y0 += dy/2;
                        break;
                    case "top":
                    case "bottom":
                        dx = d_model.width / d_dock.numOfPorts;
                        dy = 0;
                        x0 += dx/2;
                        break;
                }
                let alignment_baseline;
                let text_anchor;
                switch (d_dock.orientation) {
                    case "left":
                        alignment_baseline = "central";
                        text_anchor = "start";
                        break;
                    case "right":
                        x0 += d_model.width;
                        alignment_baseline = "central";
                        text_anchor = "end";
                        break;
                    case "top":
                        alignment_baseline = "hanging";
                        text_anchor = "middle";
                        break;
                    case "bottom":
                        y0 += d_model.height;
                        alignment_baseline = "ideographic";
                        text_anchor = "middle";
                        break;
                }
                ports.select(".port_name")
                    .attr("x", function(d,i){
                        return x0 + i * dx + obj.text_offset[d_dock.orientation][0];
                    })
                    .attr("y", function(d,i){
                        return y0 + i * dy + obj.text_offset[d_dock.orientation][1];
                    })
                    .text(function(d) { return d.value.name; })
                    .attr("text-anchor", text_anchor)
                    .attr("alignment-baseline", alignment_baseline);

                ports.select(".arrow")
                    .attr("points", function(d,i){
                        let y = y0 + i * dy;
                        let x = x0 + i * dx;
                        d.linepoint = [form[6] + x, form[7] + y];
                        return "X1,Y1 X2,Y2 X3,Y3"
                            .replace("X1", form[0] + x)
                            .replace("Y1", form[1] + y)
                            .replace("X2", form[2] + x)
                            .replace("Y2", form[3] + y)
                            .replace("X3", form[4] + x)
                            .replace("Y3", form[5] + y);
                    });
            });
        });
    }

    async get_model_by_id(mu_id){
        return main.select("#mu_"+mu_id)
    }


    async add(name, fk_model){
        await post("add_mu",
            {
                'name': name,
                'fk_model': fk_model
            }, true);
    }

    async activate(mu_id){
        let g = await this.get_model_by_id(mu_id);
        await this.deactivate_all();
        g.select(".box").classed("active", true);

        view.set_mu(g.data()[0]);
    }
    async deactivate_all(){
        main.selectAll(".box").classed("active", false);
    }

    async remove(mu){
        await post("remove_mu",
            {
                'mu_id': mu.id
            }, true);
        view.set_mu(null);
    }

    modelToFront(model){
        d3.selectAll(".connection").each(function(d,i){
            model.parentNode.appendChild(model);
        });
        model.parentNode.parentNode.appendChild(model.parentNode);
    }

    async onModelDrag() {
        let obj = this;
        return d3.drag()
            .on("start", await async function (mu) {
                d3.select(this).classed("box_dragging", true);
            })
            .on("drag", await async function (d) {
                d.x += d3.event.dx;
                d.y += d3.event.dy;
                await update_all();
            })
            .on("end", await async function (d) {
                await post("set_mu_pos",
                    {
                        'mu_id': d.id,
                        'x': d.x,
                        'y': d.y
                    }, false);
                d3.select(this).classed("box_dragging", false);
            })
    }

    async onPortDrag(){

        return d3.drag()
            .on("start", await async function (d) {
                let model = this.parentNode.parentNode.parentNode;
                d3.selectAll(".connection").each(function(d,i){
                    this.parentNode.appendChild(this);
                });
                model.parentNode.appendChild(model);
                d3.select(model).select(".box").classed("box_dragging", true);
            })
            .on("drag", await async function (d) {
                let d_model = this.parentElement.parentElement.parentElement.__data__;
                d_model.x += d3.event.dx;
                d_model.y += d3.event.dy;
                await update_all();
            })
            .on("end", await async function (d) {
                let model = this.parentNode.parentNode.parentNode;
                let d_model = model.__data__;
                await post("set_mu_pos",
                    {
                        'mu_id': d_model.id,
                        'x': d_model.x,
                        'y': d_model.y
                    }, false);
                d3.select(model).select(".box").classed("box_dragging", false);
            })
    }

    async onModelResize() {
        return d3.drag()
            .on("start", async function (d) {})
            .on("drag", async function (d) {
                d.width = Math.max(d.width+d3.event.dx,30);
                d.height = Math.max(d.height+d3.event.dy,30);
                await update_all();
            })
            .on("end", async function (d) {
                await post("set_mu_size",
                    {
                        'mu_id': d.id,
                        'width': d.width,
                        'height': d.height
                    }, false);
            })
    }

    async onConnecting(){
        return d3.drag()
            .on("start", async function (d) {await connecting_start(this, d)})
            .on("drag", async function (d) {await connecting_drag(this, d)})
            .on("end", async function (d) {await connecting_end(this, d)});

        async function connecting_start(arrow, d){
            d3.select(arrow.parentElement).select('.port_name').text(d.name + ' [' + d.unit + ']');

            d3.select(".main").append("line")
                .classed("connecting_line", true)
                .attr("x1", d.linepoint[0])
                .attr("y1", d.linepoint[1])
                .attr("x2", d.linepoint[0])
                .attr("y2", d.linepoint[1]);

            let direction_1 = arrow.parentElement.parentElement.__data__.direction;

            d3.selectAll(".line").on("mouseover", null);

            d3.select(arrow)
                .classed("connecting_from", true);

            d3.selectAll('.arrow')
                .filter(function(d, i) {return this.parentElement.parentElement.__data__.direction !== direction_1;})
                .classed("port_selectable", true);


            d3.selectAll('.port_selectable')
                .filter(function(d, i) {return d.model === d3.select(".connecting_from").data()[0].model;})
                .classed("port_selectable", false);

            d3.selectAll('.port_selectable')
                .on("mouseover", function(d) {
                    d3.select(this.parentElement).select('.port_name').text(d.name + ' [' + d.unit + ']');
                    d3.select(this).classed("connecting_to", true);
                })
                .on("mouseout", function(d) {
                    d3.select(this.parentElement).select('.port_name').text(d.name);
                    d3.select(this).classed("connecting_to", false);
                });
        }

        async function connecting_drag(arrow,d){
            if (d3.select(".connecting_to").empty()) {
                let pos = d3.mouse(arrow);
                d3.select(".connecting_line")
                    .classed('active', false)
                    .attr("x2", pos[0])
                    .attr("y2", pos[1]);
            } else {
                d3.select(".connecting_line")
                    .classed('active', true)
                    .attr("x2", d3.select(".connecting_to").data()[0].linepoint[0])
                    .attr("y2", d3.select(".connecting_to").data()[0].linepoint[1]);
            }
        }

        async function connecting_end(arrow,d){
            d3.select(arrow.parentElement).select('.port_name').text(d.name);
            d3.select(".connecting_line").remove();

            if (!d3.select(".connecting_to").empty()) {
                await connections.add(d3.select(".connecting_from"), d3.select(".connecting_to"));
            }

            d3.selectAll('.connecting_to').classed("connecting_to", false);
            d3.selectAll('.connecting_from').classed("connecting_from", false);

            d3.selectAll('.port_choice1').classed("port_choice1", false).classed("port", true);
            d3.selectAll('.port_inselectable').classed("port_inselectable", false).classed("port", true);
            d3.selectAll('.port_selectable').classed("port_selectable", false).classed("port", true);
            d3.selectAll('.port').on("mouseover", null).on("mouseout", null);

            d3.selectAll(".line").on("mouseover", function(d){d3.select(this).classed("line_hover",true);});


        }
    }




    get_port_arrow_form(orientation, direction, size) {
        let form = [[-size/1.5,0],[size/1.5,0],[0,size],[0,size]]; // bottom , out

        //    ________
        //   |        |
        //   |________|
        //       \/
        //

        if (direction === 'input') { // top, out
            for (let i = 0; i < form.length-1; i++) {
                form[i][1] = size - form[i][1];
            }
        }
        let temp;
        for (let i = 0; i < form.length; i++) {
            switch (orientation) {
                case "left": // turn to left
                    temp = form[i][0];
                    form[i][0] = 0-form[i][1];
                    form[i][1] = 0-temp;
                    break;
                case "right": // turn to right
                    temp = form[i][0];
                    form[i][0] = form[i][1];
                    form[i][1] = temp;
                    break;
                case "top": // flip to bottom
                    form[i][0] = 0 - form[i][0];
                    form[i][1] = 0 - form[i][1];
                    break;
            }
        }
        return [form[0][0],form[0][1],form[1][0],form[1][1],form[2][0],form[2][1],form[3][0],form[3][1]];
    }
}