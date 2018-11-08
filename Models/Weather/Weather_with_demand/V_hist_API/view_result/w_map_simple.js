class W_map_simple {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.run = 0;

        // Margin
        this.margin = {top: 50, right: 50, bottom: 50, left: 100};
        this.width = window.innerWidth - this.margin.left - this.margin.right;
        this.height = parent.node().getBoundingClientRect().height - this.margin.top - this.margin.bottom;

        // Elements
        this.svg = parent.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom);

        this.g = this.svg.append("g");

        // Volcano
        this.volcano = new Volcano(this);

    }

    async updateData() {
        let obj = this;

        // data of volcano
        let data_volcano = await d3.json(data_url_volcano);
        if (data_volcano) {
            this.data_volcano = data_volcano;
        }
    }

    async updateView(updateSpeed){
        if (this.data_volcano){
            this.volcano.data = this.data_volcano;
        }
    }

}