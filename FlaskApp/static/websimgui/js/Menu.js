class Menu {
    constructor(parent) {
        this.parent = parent;

        let obj = this;
        this.menu = parent.append("div")
            .attr("id", "wsg_menu");

        this.menu.append("img")
            .attr("id", "btn_fullscreen")
            .attr("src","static/images/icons/arrows_out.png")
            .on("click", async function() {
                let isfullscreen = obj.parent.classed("full-screen");
                let arrow = isfullscreen ? "out" : "in";
                d3.select("#btn_fullscreen").attr("src","static/images/icons/arrows_"+arrow+".png");
                obj.parent.classed("full-screen",!isfullscreen);
            });

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

        this.menu.append("img")
            .attr("id", "btn_update")
            .attr("src","static/images/icons/update.png")
            .on("click", async function() {
                let shadow = d3.select("#wsg_drawing").append("rect")
                    .attr("id", "shadow")
                    .style("width", "100%")
                    .style("height", "100%")
                    .style("fill", "white")
                    .style("opacity", 0.5);
                await post("update", {},true);
                obj.update();
                shadow.remove();
            });

       this.menu.append("img")
            .attr("id", "btn_add_model")
            .attr("src","static/images/icons/plus.png")
            .on("click", async function() {
                await popup_addModel.up();
                obj.update();
            });


       let h_start;
       let pos_start;
       this.menu.append("img")
            .attr("id", "btn_add_model")
           .attr("src","static/images/icons/resize_vertical.png")
           .attr("width", 30)
           .attr("height", 30)
           .call(  d3.drag()
                   .on("start", async function () {
                       h_start = parseInt(d3.select("#wsg_drawing").style('height'));
                       pos_start = d3.mouse(d3.select("body").node())[1];
                   })
                   .on("drag", async function () {
                       let h = h_start + d3.mouse(d3.select("body").node())[1] - pos_start;
                       h = (h<0) ? 0 : h;
                       d3.select("#wsg").style('grid-template-rows', h + 'px 40px auto');
                   })
           );

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