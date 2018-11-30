class EN_Tiers {
    constructor(parentObj) {
        this.parentObj = parentObj;
        this.run = 0;

        // Margin
        this.margin = {top: 100, right: 100, bottom: 170, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = 800; //parentObj.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // Elements
        this.svg = parentObj.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom);

        this.axis = new Axis_Tiers(this.svg, 100, 100, this.width, this.height);
        this.axis.xLabelLeft = "Production";
        this.axis.xLabelRight = "Consumption";
        this.axis.yLabel = "Weights";

        this.line = new Line_Tiers(this.axis);

        this.legend = new Legend_Tiers(this.axis, 0, this.height + 140);

    }


    async setDistNet(id) {
        this.Stao_ID = id;
        this.run = 0;
        await this.updateData();
        await this.updateView();
    }

    async updateData() {
        let obj = this;

        let filter = {
            'stao': ["el_rate", "Stao_ID"],
            'data': ["el_rate", "border_lines"]
        };

        //filter = {};
        let data_dict = {'mu_id': mu_id, 'mu_run': this.run, 'filter': filter};
        let data = await get(data_dict);
        data = JSON.parse(data);

        // select stao
        let i_stao = -1;
        if (data) {
            i_stao = data.result.stao.findIndex(function (i) {
                return i === obj.Stao_ID;
            });
        }

        if (data && i_stao >= 0) {
            this.run = data.run;

            let data_stao = {
                Stao_ID: data.result.stao[i_stao],
                borders: data.result.data.borders[i_stao],
                tier_values: [data.result.data.tier_values[0][i_stao], data.result.data.tier_values[1][i_stao]]
            };

            // Level labels (legend)
            let labels = data.result.data.tiers;

            // Data
            this.data = labels.map(function (c, id_c) {
                return {
                    id: id_c,
                    label: c,
                    values: data_stao.borders.map(function (d, id_d) {
                        return {
                            x: d,
                            y: data_stao.tier_values[id_c][id_d]
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


class Axis_Tiers {
    constructor(parent, x, y, width, height){

        this.updateSpeed=200;

        this.xScale = d3.scaleLinear().range([0, width]);
        this.yScale = d3.scaleLinear().range([height, 0]);

        this.zScale = d3.scaleOrdinal(d3.schemeCategory10);

        this.g = parent.append("g")
            .attr("transform", "translate(" + x + "," + y + ")");

        this.g.append('text').text('Tiers')
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
            .attr('text-anchor', 'start')
            .attr('alignment-baseline', 'hanging')
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
            let colors = Array.apply(0, Array(n)).map(function(d,i) { return d3.interpolateRdYlBu(i/(n-1)) });
            //let colors = Array.apply(0, Array(n)).map(function(d,i) { return d3.interpolateRdYlGn(i/(n-1)) });
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
            .attr("y", this.yScale(this.yLimits[1])+10)
            .attr("x", 10);
    }
}


class Line_Tiers {
    constructor(axis){
        this.parent = axis.g;
        this.axis = axis;

        let obj = this;

        this.line = d3.line()
            .defined(function(d) { return d.y!==undefined; })
            .x(function(d) { return obj.axis.xScale(d.x); })
            .y(function(d) { return obj.axis.yScale(d.y); });

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
        new_items.append("path").style("stroke-dasharray", function (d, i) {
            return i>0 ? 8 : 0;
        }).style("stroke-width", 4);
        //new_items.append("g").attr("class", "circles");
    }

    _update(){
        let obj = this;
        this.items.select("path")
            .transition().duration(this.updateSpeed)
            .attr("d", function(d) {return obj.line(d.values); })
            .style("stroke", function(d) {return obj.axis.zScale(d.id); });
    }
}

class Legend_Tiers {
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

