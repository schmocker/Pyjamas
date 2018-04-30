class Connection {
    constructor(fromPort, toPort, svg) {
        this.fromPort = fromPort;
        this.toPort = toPort;

        this.id = this.fromPort.id + '_TO_' + this.toPort.id;



        this.fromPort.connections[this.id] = this;
        this.toPort.connections[this.id] = this;


        this.line = svg.append("line")
            .style("stroke", "black")
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", 0);

        this.arrow = svg.append("polygon")
            .attr("class","arrow")
            .attr("points", "0,0 0,0 0,0")
    }

    updatePosition() {
        this.updateLine();
        this.updateArrow();
    }
    updateLine() {
        this.line.attr("x1", this.fromPort.linePoint[0]);
        this.line.attr("y1", this.fromPort.linePoint[1]);
        this.line.attr("x2", this.toPort.linePoint[0]);
        this.line.attr("y2", this.toPort.linePoint[1]);
    }
    updateArrow() {
        var vec = [this.line.attr("x2") - this.line.attr("x1"), this.line.attr("y2") - this.line.attr("y1")];
        var length = Math.sqrt(Math.pow(vec[0], 2) + Math.pow(vec[1], 2));

        var norm = [vec[0] / length, vec[1] / length];


        var len = 20;
        var arrow_Tail = [(Number(this.line.attr("x1")) + Number(this.line.attr("x2"))) / 2 - len / 2 * norm[0], (Number(this.line.attr("y1")) + Number(this.line.attr("y2"))) / 2 - len / 2 * norm[1]];

        var arrow_Point = [arrow_Tail[0] + len * norm[0], arrow_Tail[1] + len * norm[1]];
        var arrow_Left = [arrow_Tail[0] - len / 2 * norm[1], arrow_Tail[1] + len / 2 * norm[0]];
        var arrow_Right = [arrow_Tail[0] + len / 2 * norm[1], arrow_Tail[1] - len / 2 * norm[0]];
        var attr = "" + arrow_Point[0] + "," + arrow_Point[1] +
            " " + arrow_Left[0] + "," + arrow_Left[1] +
            " " + arrow_Right[0] + "," + arrow_Right[1];
        this.arrow.attr("points", attr);
    }
}
