class Popup {
    constructor(parent, name) {
        this.id = "popup_" + name;
        let obj = this;

        this.popup = parent.append("div")
            .attr("id", this.id)
            .classed("popup",true)
            .on("click", function() { obj.hide() });

        let frame = this.popup.append("div")
            .classed("frame",true)
            .on("click", function() { d3.event.stopPropagation(); });


        frame.append("span")
            .classed("close",true)
            .html('&#215;')
            .on("click",function(){ obj.hide() });

        this.popup_content = frame.append("div")
            .classed("popup_content",true);


    }

    set content(content){
        this.popup_content.html(content);
    }

    show(){
        this.popup.style("display", "block");
    }

    hide(){
        this.popup.style("display", "none");
    }

    async up(){
        this.content("default content");
        this.show()
    }

}

class Popup_model_docu extends Popup{
    constructor(parent) {
        super(parent, "model_docu");
    }

    async up(model_id){
        this.content =  await get('get_model_readme',{'model': model_id});
        this.show()
    }
}

class Popup_model_properties_view extends Popup{
    constructor(parent) {
        super(parent, "model_view");
    }

    async up(d){
        let props = await get('get_model_properties_view',{'model': d.id});

        // TODO: Check if props is html, else make standart html for props
        this.content =  "";
        if (true) {
            let content = this.popup_content;

            content.append("h2").text("Properties");
            let form = content.selectAll(".propertiesForm").data([d]);
            form = form.enter().append("g")
                .classed("properties", true)
                .attr("name","properties");

            let props = form.selectAll(".property").data(function (d) {return d3.entries(d.model.info.properties)});
            props = props.enter().append("g")
                .classed("property", true);
            props.append("span").html(function (d, i) {
                let brake = (i===0 ? '' : '<br>');
                return brake + d.value.name + ':<br>';
            });
            let obj = this;
            props.append("input")
                .attr("id",function (d) {
                    return d.key;
                })
                .attr("name",function (d) {
                    return d.key;
                })
                .attr("type","text")
                .attr("value","")
                .on("input", function(d) {
                    obj.submit(d.key, this.value);
                    this.value = this.value.replace(/[^\d.-]/g, '');
                })
                .on('keyup', function (d) {
                    if (d3.event.keyCode === 13) {
                        obj.submit(d.key, this.value)
                    }
                })
                .on('blur', function (d) {
                    obj.submit(d.key, this.value)
                });
            props.append("br");
        } else {
            this.content =  props;
        }
        this.show()
    }

    submit(key, value){
        let id_model_used = d3.select('.properties').data()[0].id;
        post('set_model_property', {'model': id_model_used, 'property': key, 'value': value})
    }
}

class Popup_model_results_view extends Popup{
    constructor(parent) {
        super(parent, "model_view");
    }

    async up(model_id){
        let results_html = await get('get_model_results_view',{'model': model_id});

        this.content =  results_html;
        this.show()
    }
}


class Popup_addModel extends Popup{
    constructor(parent) {
        super(parent, "add_model");
        let obj = this.popup_content;
        obj = obj.append("from").attr("name","addBoxForm");
        obj.append("span").html('Model Name:<br>');
        obj.append("input")
            .attr("id","model_name")
            .attr("name","model_name")
            .attr("type","text")
            .attr("value","");
        obj.append("span").html('<br>Topic:<br>');
        obj.append("select")
            .attr("id","topic_selection")
            .attr("name","topic_selection");
        obj.append("span").html('<br>Model:<br>');
        obj.append("select")
            .attr("id","model_selection")
            .attr("name","model_selection");
        obj.append("span").html('<br>Version:<br>');
        obj.append("select")
            .attr("id","version_selection")
            .attr("name","version_selection");
        obj.append("span").html('<br>');
        let kkk = this;
        obj.append("input")
            .attr("type","submit")
            .attr("value","Submit")
            .on("click",function(){kkk.validateForm()});
    }



    async up(){
        d3.select("#model_name").property("value","");
        d3.select("#varsion_selection").selectAll("option").remove();

        let all_models = await $.get("/websimgui", {
            'fnc': 'get_model_selection',
            'data': JSON.stringify({})});
        all_models = JSON.parse(all_models);

        d3.select("#topic_selection")
            .on('change', function(){
                let d = d3.select("#topic_selection").property("selectedOptions")[0].__data__;
                d3.select("#model_selection").selectAll("option").remove();

                let objs = d3.select("#model_selection").selectAll(".model_option").data(d3.entries(d.value));
                objs.enter()
                    .append("option")
                    .classed("model_option",true)
                    .attr("value",function (d) {return d.key})
                    .text(function (d) {return d.key});

                d3.select("#model_selection").dispatch('change');
            });

        d3.select("#model_selection")
            .on('change', function(){
                let d = d3.select("#model_selection").property("selectedOptions")[0].__data__;
                d3.select("#version_selection").selectAll("option").remove();

                let objs = d3.select("#version_selection").selectAll(".version_option").data(d3.entries(d.value));
                objs.enter()
                    .append("option")
                    .classed("version_option",true)
                    .attr("value",function (d) {return d.key})
                    .text(function (d) {return d.key});
            });

        all_models = d3.entries(all_models);


        d3.select("#topic_selection").selectAll("option").remove();
        let objs = d3.select("#topic_selection").selectAll(".topic_option").data(all_models);
        objs.enter()
            .append("option")
            .classed("topic_option",true)
            .attr("value",function (d) {return d.key})
            .text(function (d) {return d.key});

        d3.select("#topic_selection").dispatch('change');



        this.show()
    }





    async validateForm() {
        let boxName = d3.select("#model_name").property("value");

        let v = d3.select("#version_selection").property("selectedOptions")[0].__data__;
        let model_id = v.value.id;

        if (boxName == "") {
            d3.select("#model_name").style("background-color","red");
            return false;
        }
        let modal = document.getElementById('myModal');
        this.hide();
        await models.add(boxName, model_id);
    }
}