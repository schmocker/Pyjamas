class Menu {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.menu = parent.append("div")
            .attr("id", "wsg_menu");

        this.menu.append("img")
            .attr("id", "btn_fullscreen")
            .attr("src","static/images/icons/arrows_out.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                let isfullscreen = obj.parent.classed("full-screen");
                let arrow = isfullscreen ? "out" : "in";
                d3.select("#btn_fullscreen").attr("src","static/images/icons/arrows_"+arrow+".png");
                obj.parent.classed("full-screen",!isfullscreen);
            });

        this.menu.append("img")
            .attr("id", "btn_play")
            .attr("src","static/images/icons/Play.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("start", {},false);
                obj.update();
            });

        this.menu.append("img")
            .attr("id", "btn_pause")
            .attr("src","static/images/icons/Pause.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("pause", {},false);
                obj.update();
            });

        this.menu.append("img")
            .attr("id", "btn_stop")
            .attr("src","static/images/icons/Stop.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("stop", {},false);
                obj.update();
            });

        this.menu.append("img")
            .attr("id", "btn_update")
            .attr("src","static/images/icons/update.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("update", {},true);
                obj.update();
            });

       this.menu.append("img")
            .attr("id", "btn_add_model")
            .attr("src","static/images/icons/plus.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await popup_addModel.popup();
                obj.update();
            });

       this.update()

    }

    update(){
        let newOpacity = agent_data.active ? 0 : 1;

        this.menu.select("#btn_add_model").style("opacity", newOpacity);
        this.menu.select("#btn_play").style("opacity", newOpacity);

        newOpacity = 1 - newOpacity;
        this.menu.select("#btn_pause").style("opacity", newOpacity);
        this.menu.select("#btn_stop").style("opacity", newOpacity);

    }

}