class Menu {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        menu = parent.append("div")
            .attr("id", "wsg_menu");

        menu.append("img")
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

        menu.append("img")
            .attr("src","static/images/icons/Play.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("start", {},false);
            });

        menu.append("img")
            .attr("src","static/images/icons/Pause.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("pause", {},false);
            });

        menu.append("img")
            .attr("src","static/images/icons/Stop.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("stop", {},false);
            });

        menu.append("img")
            .attr("src","static/images/icons/update.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await post("update", {},true);
            });

       menu.append("img")
            .attr("src","static/images/icons/plus.png")
            .attr("width", 30)
            .attr("height", 30)
            .on("click", async function() {
                await popup_addModel.popup()
            });

    }

}