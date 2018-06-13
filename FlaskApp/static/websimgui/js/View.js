class View {
    constructor(parent) {
        let obj = this;
        this.parent = parent;
        this.view = this.parent.append('div')
            .attr('id', 'view');
        this.title = this.view.append('div')
            .attr('id', 'view_title');

        this.menu = this.view.append('div')
            .attr('id', 'view_menu');
        this.menu.append('div')
            .classed("view_menu_item", true)
            .classed("active", true)
            .attr('id', 'docu')
            .html("Documentation")
            .on('click', async function () {
                await obj.update_menu(this);
                await obj.update_docu();
            });
        this.menu.append('div')
            .classed("view_menu_item", true)
            .attr('id', 'properties')
            .html("Properties")
            .on('click', async function () {
                await obj.update_menu(this);
                await obj.update_default_property_view();
            });
        this.menu.append('div')
            .classed("view_menu_item", true)
            .attr('id', 'results')
            .html("Results")
            .on('click', async function () {
                await obj.update_menu(this);
                await obj.update_results();
                log("results")
            });
        this.menu.append('div')
            .classed("view_menu_item", true)
            .attr('id', 'remove')
            .html("Remove")
            .on('click', async function () {
                await models.remove(obj.mu)
            });

        this.content = this.view.append('div')
            .attr('id', 'view_content');

        this.mu = null;
        this.set_mu(null)

    }

    set_mu(mu){
        let obj = this;
        this.mu = mu;
        this.update_title();

        this.menu.select("#properties")
            .html("Properties")
            .on('click', async function () {
                await obj.update_menu(this);
                await obj.update_default_property_view();
            });

        let sel = this.menu.select(".active");
        if (!sel.empty()){
            let id = sel.attr("id");
            $("#"+id).trigger("click")
        }
    }

    update_title(){
        if (this.mu===null){ this.title.html("no model selected")}
        else {
            this.title.html('Model <b>'+this.mu.name+'</b> ('+this.mu.model.topic+'/'+
                this.mu.model.name+'/'+ this.mu.model.version+')');
        }
    }

    async update_menu(menu_item){
        let obj = this;
        this.menu.selectAll(".view_menu_item").classed("active", false);
        d3.select(menu_item).classed("active", true);

        if (d3.select(menu_item) !== this.menu.select("#properties")) {
            this.menu.select("#properties")
            .html("Properties")
            .on('click', async function () {
                await obj.update_menu(this);
                await obj.update_default_property_view();
            });
        }
    }

    async update_docu(){
        if (this.mu===null){
            this.content.html("");
            return
        }
        let obj = this;
        let html = await get('get_model_readme',{'mu_id': obj.mu.id});
        this.content.html(html);
    }

    async update_results(){
        this.content.html("results will follow soon");
    }

    async update_default_property_view(){
        let obj = this;
        this.content.html("");

        let prop_data = await get('get_model_properties',{'model': obj.mu.id});
        prop_data = JSON.parse(prop_data);
        if (obj.mu.model.has_property_view){
            this.menu.select("#properties")
                .html("Custom Properties")
                .on('click', async function () {
                    await obj.update_menu(this);
                    await obj.set_custom_property_view();
                });
        }
        let form = this.content.selectAll(".propertiesForm").data([obj.mu]);
        form = form.enter().append("g").classed("properties", true).attr("name","properties");

        let props = form.selectAll(".property").data(function (mu) {return d3.entries(mu.model.info.properties)});
        props = props.enter().append("g").classed("property", true);
        props.append("span").html(function (d, i) {
            let brake = (i===0 ? '' : '<br>');
            return brake + d.value.name + ':<br>';
        });
        props.append("input")
            .attr("id",function (d) {
                return d.key;
            })
            .attr("name",function (d) {
                return d.key;
            })
            .attr("type","text")
            .attr("value",function (d) {
                return prop_data[d.key]
            })
            .on("input", function(d) {
                this.value = this.value.replace(/[^\d.-]/g, '');
                obj.submit(d.key, this.value);
            })
            .on('keyup', function (d) {
                if (d3.event.keyCode === 13) {obj.submit(d.key, this.value)}
            })
            .on('blur', function (d) {
                obj.submit(d.key, this.value)
            });
        props.append("br");
    }

    async set_custom_property_view(){
        let obj = this;
        this.content.html("");
        let src = '/model_view?MU_id='+this.mu.id+'&view=properties';
        this.menu.select("#properties")
            .html("Default Properties")
            .on('click', async function () {
                await obj.update_menu(this);
                await obj.update_default_property_view();
            }).append("img")
            .attr("src","static/images/icons/open.png")
            .style("width", "14px").style("height", "14px").style("margin-left", "15px")
            .on("click", function() { window.open(src); });
        this.content.append("div") .style("height", "500px")
            .html('<iframe src="'+src+'" width="100%" height="100%" ></iframe>');
    }
}
