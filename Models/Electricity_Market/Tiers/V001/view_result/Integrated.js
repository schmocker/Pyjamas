class Integrated {
    constructor(parentObj) {
        this.parentObj = parentObj;
        this.run = 0;
        this.data = [];

        // Margin
        this.margin = {top: 100, right: 100, bottom: 170, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = 800;

        // Elements
        this.svg = parentObj.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom);

        this.axis = new Axis_Int(this.svg, 100, 100, this.width, this.height);
        this.axis.xLabelLeft = "Production";
        this.axis.xLabelRight = "Consumption";
        this.axis.yLabel = "Costs [€/MWh]";


        this.line = new Line_Int(this.axis);

        //this.legend = new Legend_Int(this.axis, 0, this.height + 140);
        this.legend = new Legend_Int(this.axis, 0, 0);


    }

    async setDistNet(id) {
        this.Stao_ID = id;
        this.run = 0;
        await this.updateData();
        await this.updateView();
    }

    async updateData() {

        let obj = this;

        // select time
        let i_time = 0;

        // Staos
        let filter = {'orte': ['el_rate', 'Stao_ID']};

        //let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data_dict = {'mu_id': mu_id, 'mu_run': 0, 'filter': filter};
        let dict_stao = await get(data_dict);
        dict_stao = JSON.parse(dict_stao);
        let list_stao = dict_stao.result.orte;

        // select stao
        let data;
        let i_stao = -1;
        if (list_stao) {
            i_stao = list_stao.findIndex(function (i) {
                return i === obj.Stao_ID;
            });

            // get data
            filter = {'borders': ['el_rate', 'borders', i_stao],
                      'values': ['el_rate', 'values', i_stao, i_time],
                      'prices': ['el_rate', 'border_lines', 'prices', i_stao, i_time],
                      'prices_border': ['el_rate', 'border_lines', 'borders', i_stao],
                      'y_scaling': ['y_scaling'],
                      'y_label': ['y_label']
            };

            let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
            data = await get(data_dict);
            data = JSON.parse(data);
        }

        if (data && i_stao >= 0) {
            this.run = data.run;
            let y_scaling = data.result.y_scaling;

            let data_stao = {
                Stao_ID: list_stao[i_stao],
                borders: data.result.borders,
                values: data.result.values,
                prices: data.result.prices,
                prices_borders: data.result.prices_border
            };

            // Level labels (legend)
            //let labels = ["Consumption", "Consumption_bar", "Production_bar", "Production"];
            let labels = ["Consumption costs", "Consumption price", "Production price", "Production costs"];
            this.data.label = labels;

            // Cost per energy
            let borders_wo0 = data_stao.borders.borders.filter(function(val) {
                return val !== 0;
            });
            let v_values = data_stao.values.map(function (c) {return c*y_scaling});

            // divide into consumption and production
            let cons_val = [];
            let cons_border = [];
            let prod_val = [];
            let prod_border = [];
            v_values.filter(function (c, id_c) {
                if (c>=0) {
                    cons_val.push(c);
                    cons_border.push(borders_wo0[id_c]);
                } else {
                    prod_val.push(c);
                    prod_border.push(borders_wo0[id_c]);
                }
            });

            // add point near axis x = 0
            let x_point = 0.0001; // have to be smaller than first border
            cons_val.unshift(cons_val[0]);
            cons_border.unshift(x_point);
            prod_val.push(prod_val[prod_val.length-1]);
            prod_border.push(-x_point);

            let cons_border_0 = [0].concat(cons_border);
            let prod_border_0 = prod_border.concat(0);
            let cons_borderwidth = diff(cons_border_0);
            let prod_borderwidth = diff(prod_border_0);

            let cons_area = cons_borderwidth.map(function (c, id_c) {
               return c * cons_val[id_c];
            });
            let prod_area = prod_borderwidth.map(function (c, id_c) {
               return c * prod_val[id_c];
            });

            let cons_area_sum = [];
            cons_area.reduce(function(a,b,i) { return cons_area_sum[i] = a+b; },0);
            let cons_cost = cons_area_sum.map(function (c, id_c) {
                return c / cons_border[id_c];
            });

            let prod_area_inv = prod_area.map(function (c, id_c) {
               return prod_area[prod_area.length-(id_c+1)];
            });
            let prod_area_sum_inv = [];
            prod_area_inv.reduce(function(a,b,i) { return prod_area_sum_inv[i] = a+b; },0);
            let prod_area_sum = prod_area_sum_inv.map(function (c, id_c) {
               return prod_area_sum_inv[prod_area_sum_inv.length-(id_c+1)];
            });
            let prod_cost = prod_area_sum.map(function (c, id_c) {
                return c / Math.abs(prod_border[id_c]);
            });


            // prices
            let prices = data_stao.prices.map(function (c) {return c*y_scaling});
            let pr_cons_val = [];
            let pr_cons_border = [];
            let pr_prod_val = [];
            let pr_prod_border = [];
            prices.filter(function (c, id_c) {
                if (c>=0) {
                    pr_cons_val.push(c);
                    pr_cons_border.push(data_stao.prices_borders[id_c]);
                } else {
                    pr_prod_val.push(c);
                    pr_prod_border.push(data_stao.prices_borders[id_c]);
                }
            });

            // data
            let costs = [cons_cost, pr_cons_val, pr_prod_val, prod_cost];
            let borders_array = [cons_border, pr_cons_border, pr_prod_border, prod_border];

            this.data = labels.map(function (c, id_c) {
               return {
                   id: id_c,
                   label: c,
                   values: costs[id_c].map(function (d, id_d) {
                       return {
                           x: borders_array[id_c][id_d],
                           y: d
                       }
                   })
               }
            });

            this.data.label = labels;
        }
    }

    async updateView(updateSpeed) {
        if (this.data) {
            let x_min = d3.min(this.data, function (c) {
                return d3.min(c.values, function (d) {
                    return d.x;
                });
            });
            let x_max = d3.max(this.data, function (c) {
                return d3.max(c.values, function (d) {
                    return d.x;
                });
            });
            this.axis.xLimits = [x_min, x_max];

            let y_min = d3.min(this.data, function (c) {
                return d3.min(c.values, function (d) {
                    return d.y;
                });
            }) * 1.05;
            let y_max = d3.max(this.data, function (c) {
                return d3.max(c.values, function (d) {
                    return d.y;
                });
            }) * 1.05;
            this.axis.yLimits = [d3.min([0, y_min]), d3.max([0, y_max])];

            this.axis.zLimits = this.data.label;

            this.line.data = this.data;
            this.legend.data = this.data.label;
        }
    }
}

function diff(A) {
    return A.slice(1).map(function (n,i) {return Math.abs(n-A[i]);});
}

class Axis_Int {
    constructor(parent, x, y, width, height){

        this.updateSpeed=200;

        this.xScale = d3.scaleLinear().range([0, width]);
        this.yScale = d3.scaleLinear().range([height, 0]);

        this.zScale = d3.scaleOrdinal(d3.schemeCategory10);

        this.g = parent.append("g")
            .attr("transform", "translate(" + x + "," + y + ")");

        this.g.append('text').text('Costs')
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + width/2 + ",-20)");

        this.xAxis = this.g.append("g")
            .attr("class", "axis axis--x")
            .attr("transform", "translate(0," + height + ")");

        this._xLabelLeft = this.xAxis.append("text")
            .attr('class', 'xLabelL')
            .style("fill", "#000")
            .attr("text-anchor", "start");

        this._xLabelRight = this.xAxis.append("text")
            .attr('class', 'xLabelR')
            .style("fill", "#000")
            .attr("text-anchor", "end");

        this.yAxis = this.g.append("g")
            .attr("class", "axis axis--y");

        this._yLabel = this.yAxis.append("text")
            .attr('class', 'yLabel')
//            .attr('text-anchor', 'start')
            .attr('text-anchor', 'end')
//            .attr('alignment-baseline', 'hanging')
            .attr('alignment-baseline', 'middle')
            //.attr("transform", "rotate(-90)")
            //.attr("y", -70)
            //.attr("x",0- (height / 2))
            .style("fill", "#000");
    }

    set xLabelLeft(xLabelLeft){
        this._xLabelLeft.text(xLabelLeft);
    }
    set xLabelRight(xLabelRight){
        this._xLabelRight.text(xLabelRight);
    }
    set yLabel(yLabel){
        this._yLabel.text(yLabel);
    }
    set xLimits(xLimits){
        this.xScale.domain(xLimits);
        this.updateXAxis();
    }
    get xLimits(){
        return this.xScale.domain();
    }
    set yLimits(yLimits){
        this.yScale.domain(yLimits);
        this.updateYAxis();
    }
    get yLimits(){
        return this.yScale.domain();
    }
    set zLimits(zLimits){
        try {
            let n = zLimits.length;
            //let colors = Array.apply(0, Array(n)).map(function(d,i) { return d3.interpolateRdYlBu(i/(n-1)) });
            let colors = Array.apply(0, Array(n)).map(function(d,i) { return d3.interpolateRdYlGn(i/(n-1)) });
            this.zScale = d3.scaleOrdinal(colors);
            this.zScale.domain(zLimits);
        } catch (e) {
            console.warn(e);
        }
    }

    updateXAxis(){
        this.xAxis
            .transition().duration(this.updateSpeed)
            .call(d3.axisBottom(this.xScale))
            .attr('transform', 'translate(0,' + (this.yScale(0)) + ')')
            .selectAll(".tick").selectAll("text")
            .style("text-anchor", "middle")
            .attr("dx", "0em").attr("dy", "1em");

        this.xAxis.selectAll(".xLabelL")
            .attr("y", -10)
            .attr("x", this.xScale(this.xLimits[0]));

        this.xAxis.selectAll(".xLabelR")
            .attr("y", -10)
            .attr("x", this.xScale(this.xLimits[1]));
    }

    updateYAxis(){
        this.yAxis
            .transition().duration(this.updateSpeed)
            .call(d3.axisLeft(this.yScale))
            .attr('transform', 'translate(' + (this.xScale(0)) + ',0)');

        this.yAxis.selectAll(".yLabel")
            .attr("y", this.yScale(this.yLimits[1])+0)
            .attr("x", -60);
    }
}


class Line_Int {
    constructor(axis){
        this.parent = axis.g;
        this.axis = axis;

        let obj = this;

        this.line = d3.line()
            .defined(function(d) { return d.y!==undefined; })
            .x(function(d) { return obj.axis.xScale(d.x); })
            .y(function(d) { return obj.axis.yScale(d.y); });

        this.tooltip = new ToolTip_Int(axis);

        this.updateSpeed = 500;

        this.items = null;
    }
    set data(data){
        this.items = this.parent.selectAll('.line').data(data);
        this._exit();
        this._enter();
        this.items = this.parent.selectAll('.line');
        this._update();
    }

    _exit(){
        this.items.exit().remove();
    }

    _enter(){
        let new_items = this.items.enter().append("g").attr("class", "line");
        new_items.append("path");
        new_items.append("g").attr("class", "circles");
    }

    _update(){
        let obj = this;
        this.items.select("path")
            .transition().duration(this.updateSpeed)
            .attr("d", function(d) {return obj.line(d.values); })
            .style("stroke", function(d) {return obj.axis.zScale(d.id); });

        //this.items.select('circle').remove();

        // Circles
        let circles = this.items.select(".circles").selectAll("circle")
            .data(function (d) {return d.values.filter(function(item){return item.y !== undefined}); });


        circles.exit().remove();

        circles.enter().append('circle')
            .attr("r", 3).style("opacity", 0)
            .on("mouseover", function(d) { obj.tooltip.show(d.x, d.y); })
            .on("mouseout", function() { obj.tooltip.hide(); });

        circles = this.items.select(".circles").selectAll("circle");

        circles
            .style("stroke", function() {return obj.axis.zScale(this.parentNode.__data__.id); })
            .style("fill", function() {return obj.axis.zScale(this.parentNode.__data__.id); });
        circles
            .transition().duration(this.updateSpeed)
            .attr("cx", function(d) { return obj.axis.xScale(d.x); })
            .attr("cy", function(d) { return obj.axis.yScale(d.y); });
        circles
            .transition().delay(this.updateSpeed)
            .style("opacity", 1);
    }
}

class ToolTip_Int {
    constructor(axis){
        this.axis = axis;
        this.updateSpeed = 200;

        this.g = this.axis.g.append("g")
            .attr("class", "tooltip")
            .style("opacity", 0);

        this.rect = this.g.append("rect");

        this.xVal = this.g.append("text").attr("id", "xVal");
        this.yVal = this.g.append("text").attr("id", "yVal");

        this.padding = 10;
    }

    show(xVal, yVal){

        this.g.moveToFront();

        let size = parseInt(this.g.style("font-size"));
        let x_label = 'rel. power: ' + Math.round(xVal*100)/100;
        let y_label = 'cost: ' + Math.round(yVal*100)/100 + ' €/MWh';
        this.xVal.text(x_label)
            .attr("y",size);
        this.yVal.text(y_label)
            .attr("y",2.5*size);

        let height = 2.5*size;

        let wx = this.xVal.node().clientWidth;
        let wy = this.yVal.node().clientWidth;
        let width = Math.max(wx,wy);

        this.rect
            .attr("x",-this.padding)
            .attr("y",-this.padding)
            .attr("width", width+2*this.padding)
            .attr("height", height+2*this.padding);

        this.g
            .attr("transform", "translate(" + (this.axis.xScale(xVal)-width/2) + "," + (this.axis.yScale(yVal)-10-this.padding-height) + ")")
            .transition().duration(this.updateSpeed)
            .style("opacity", .9);
    }

    hide(){
        this.g.transition()
            .duration(this.updateSpeed)
            .style("opacity", 0);
    }
}


class Legend_Int {
    constructor(axis, x, y) {
        this.axis = axis;

        this.g = axis.g.append("g").attr('class', 'legend');
        this.items = null;

        //let wx = this.xVal.node().clientWidth;
        this.x = x;
        this.dx = 0;
        this.dy = 30;
        this.y = y;
        this.size = 10;
        this.updateSpeed = 0;

    }

    get data() {
        this.g.selectAll(".item").data();
    }

    set data(data) {
        try {
            //throw "gaht nöd";
            this.items = this.g.selectAll('.item').data(data);
            this._exit();
            this._enter();
            this.items = this.g.selectAll('.item');
            this._update();
        } catch (e) {
            throw "could not update legend data: " + e;
        }
    }

    _exit() {
        this.items.exit().remove();
    }

    _enter() {
        let new_items = this.items.enter().append('g').attr('class', 'item');
        new_items.append('rect')
            .attr('x', 0).attr('width', this.size)
            .attr('y', -this.size / 2).attr('height', this.size);
        new_items.append('text')
            .style('alignment-baseline', 'central')
            .attr('x', this.size + 5);
    }

    _update() {
        let obj = this;

        this.items.select('rect').style('fill', function (d) {
            return obj.axis.zScale(d);
        });
        this.items.select('text').text(function (d) {
            return d
        });

        /*
        let allWidths = Array.from(d3.select(".legend").selectAll(".item")._groups[0]).map(function (g) {
            return g.getBBox().width
        });
        let maxwidth_clients = d3.max(allWidths);
        let space = 20;
        if (maxwidth_clients) {
            obj.dx = maxwidth_clients + space;
        } else {
            obj.dx = 0;
        }
        */
        this.items.attr("transform", function (d, i) {
            return "translate(" + obj.x + obj.dx * i + "," + obj.y + obj.dy * i + ")"
        });
    }
}
