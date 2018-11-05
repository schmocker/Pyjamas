class Diagram {
    constructor(parent) {
        this.parent = parent;
        this.run = 0;
        this.data = [];

        // Margin
        this.margin = {top: 100, right: 100, bottom: 170, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // Elements
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom);

        this.axis = new Axis(this.svg, 100, 100, this.width, this.height);
        this.axis.xLabel = "Date";

        this.line = new Line(this.axis);

        this.legend = new Legend(this.axis, 0, this.height + 140);

    }

    async setDistNet(id) {
        this.Stao_ID = id;
        this.run = 0;
        await this.updateData();
        await this.updateView();
    }

    async updateData() {
        let obj = this;

        let filter = {};

        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(data_dict);
        data = JSON.parse(data);

        // select stao
        let i_stao = -1;
        if (data) {
            i_stao = data.result.el_rate.Stao_ID.findIndex(function (i) {
                return i === obj.Stao_ID;
            });
        }

        if (data && i_stao >= 0) {
            this.run = data.run;
            let y_scaling = data.result.y_scaling;

            let data_stao = {
                Stao_ID: data.result.el_rate.Stao_ID[i_stao],
                borders: data.result.el_rate.borders[i_stao],
                values: data.result.el_rate.values[i_stao]
            };

            // Level labels (legend)
            let l_borders = data_stao.borders.borders.length;
            let labels = [];
            let ib;
            for (ib = 0; ib < (l_borders - 1); ib++) {
                labels[ib] = "[" + data_stao.borders.borders[ib].toString() + ", " +
                    data_stao.borders.borders[ib + 1].toString() + "]";
            }

            // Data
            this.data = data_stao.values[0].map(function (c, id_c) {
                return {
                    id: id_c,
                    label: labels[id_c],
                    values: data.result.times.map(function (d, id_d) {
                        return {
                            date: new Date(d * 1E3),
                            y: data_stao.values[id_d][id_c]*y_scaling
                        }
                    })
                }
            });
            this.data.label = labels;
            this.data.yLabel = data.result.y_label;
        }
    }

    async updateView(updateSpeed) {
        //console.log(new Date());
        if (this.data) {
            this.axis.yLabel = this.data.yLabel;

            let x_min = d3.min(this.data, function (c) {
                return d3.min(c.values, function (d) {
                    return d.date;
                });
            });
            let x_max = d3.max(this.data, function (c) {
                return d3.max(c.values, function (d) {
                    return d.date;
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

class Axis {
    constructor(parent, x, y, width, height){

        this.formatTime = d3.timeFormat("%Y-%m-%d %H:%M:%S");
        this.updateSpeed=200;

        this.xScale = d3.scaleTime().range([0, width]);
        this.yScale = d3.scaleLinear().range([height, 0]);

        this.zScale = d3.scaleOrdinal(d3.schemeCategory10);

        this.g = parent.append("g")
            .attr("transform", "translate(" + x + "," + y + ")");

        this.g.append('text').text('Time Series')
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + width/2 + ",-20)");

        this.xAxis = this.g.append("g")
            .attr("class", "axis axis--x")
            .attr("transform", "translate(0," + height + ")");

        this._xLabel = this.xAxis.append("text")
            .attr('class', 'xLabel')
            .attr("y", 110)
            .attr("x", width/2)
            .style("fill", "#000")
            .text("");

        this.yAxis = this.g.append("g")
            .attr("class", "axis axis--y");

        this._yLabel = this.yAxis.append("text")
            .attr('class', 'yLabel')
            .attr("transform", "rotate(-90)")
            .attr("y", -70)
            .attr("x",0- (height / 2))
            .style("fill", "#000")
            .text("");
    }

    set xLabel(xLabel){
        this._xLabel.text(xLabel);
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
    set zLimits(zLimits){
        try {
            let n = zLimits.length;
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
            .call(d3.axisBottom(this.xScale).tickFormat(this.formatTime))
            .selectAll(".tick").selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "0em").attr("dy", "1em")
            .attr("transform", "rotate(-15)");
    }

    updateYAxis(){
        this.yAxis
            .transition().duration(this.updateSpeed)
            .call(d3.axisLeft(this.yScale));
    }
}


class Line {
    constructor(axis){
        this.parent = axis.g;
        this.axis = axis;

        let obj = this;

        this.line = d3.line()
            .defined(function(d) { return d.y!==undefined; })
            .x(function(d) { return obj.axis.xScale(d.date); })
            .y(function(d) { return obj.axis.yScale(d.y); });

        this.tooltip = new ToolTip(axis);

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
            .on("mouseover", function(d) { obj.tooltip.show(d.date, d.y); })
            .on("mouseout", function() { obj.tooltip.hide(); });

        circles = this.items.select(".circles").selectAll("circle");

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
    }
}

class ToolTip{
    constructor(axis){
        this.axis = axis;
        this.formatTime = axis.formatTime;
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
        this.xVal.text(this.formatTime(xVal))
            .attr("y",size);
        this.yVal.text(yVal)
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


class Legend {
    constructor(axis, x, y) {
        this.axis = axis;

        this.g = axis.g.append("g").attr('class', 'legend');
        this.items = null;

        //let wx = this.xVal.node().clientWidth;
        this.x = x;
        this.dx = 100;
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

        let allWidths = Array.from(d3.select(".legend").selectAll(".item")._groups[0]).map(function (g) {
            return g.getBBox().width
        });
        let maxwidth_clients = d3.max(allWidths);
        let space = 20;
        obj.dx = maxwidth_clients + space;
        this.items.attr("transform", function (d, i) {
            return "translate(" + obj.x + obj.dx * i + "," + obj.y + ")"
        });
    }

}
