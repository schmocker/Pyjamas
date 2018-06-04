class Popup_model {
    constructor(parent) {
        let obj = parent.append("div")
            .attr("id", "popup_model")
            .classed("modal",true)
            .on("click", function() {
                this.style.display = "none"
            });
        obj = obj.append("div").classed("modal-content",true);
        obj.append("span").classed("close",true)
            .html('&#215;')
            .on("click",function(){
                document.getElementById("popup_model").style.display = "none"
            });
        obj.append("span").attr("id","model_content");


    }

    async popup(id){
        d3.select("#model_name").property("value","");
        d3.select("#varsion_selection").selectAll("option").remove();

        let description = await $.get("/websimgui", {
            'agent': agent_data.id,
            'fnc': 'get_model_description',
            'data': JSON.stringify({
                        'model': id
            })});
        d3.select("#model_content").html(description);





        document.getElementById("popup_model").style.display = "block";
    }

}