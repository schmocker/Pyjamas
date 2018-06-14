class Menu {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.menu = parent.append("div")
            .attr("id", "wsg_menu");

        this.menu.append("img")
            .attr("alt", "play")
            .attr("id", "btn_play")
            .attr("src","static/images/icons/Play.png")
            .on("click", async function() {
                await post("start", {},false);
                obj.update();
            });

        this.menu.append("img")
            .attr("id", "btn_pause")
            .attr("src","static/images/icons/Pause.png")
            .on("click", async function() {
                await post("pause", {},false);
                obj.update();
            });

        this.menu.append("img")
            .attr("id", "btn_stop")
            .attr("src","static/images/icons/Stop.png")
            .on("click", async function() {
                await post("stop", {},false);
                obj.update();
            });




       this.update()

    }

    update(){
        let disp = agent_data.active ? 'none' : 'inline';

        this.menu.select("#btn_add_model").style("display", disp);
        this.menu.select("#btn_play").style("display", disp);

        disp = (disp==='none') ? 'inline' : 'none';
        this.menu.select("#btn_pause").style("display", disp);
        this.menu.select("#btn_stop").style("display", disp);
    }

}