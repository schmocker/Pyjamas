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

        let icon_size = 25;

        this.update_interval = null;
        this.interval_speed = 1;
        this.run = 0;

        let h_start;
        let pos_start;
        this.menu.append("img")
            .attr("id", "btn_add_model")
            .classed("view_menu_item", true)
            .attr("src", "static/images/icons/resize_vertical.png")
            .attr("title", "adjust view")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .call(d3.drag()
                .on("start", async function () {
                    h_start = parseInt(d3.select("#wsg_drawing").style('height'));
                    pos_start = d3.mouse(d3.select("body").node())[1];
                })
                .on("drag", async function () {
                    let h = h_start + d3.mouse(d3.select("body").node())[1] - pos_start;
                    h = (h < 0) ? 0 : h;
                    d3.select("#wsg").style('grid-template-rows', h + 'px 1fr');
                })
            );

        this.menu.append('div')
            .classed("view_menu_item", true)
            .attr('id', 'docu')
            .html("Documentation")
            .on('click', async function () {
                await obj.update_view(this, false);
            });
        this.menu.append('div')
            .classed("view_menu_item", true)
            .attr('id', 'properties')
            .html("Properties")
            .on('click', async function () {
                await obj.update_view(this, false);
            });
        this.menu.append('div')
            .classed("view_menu_item", true)
            .attr('id', 'results')
            .html("Results")
            .on('click', async function () {
                await obj.update_view(this, false);
            });

        this.menu.append("img")
            .attr("id", "add")
            .classed("view_menu_item", true)
            .classed("active", true)
            .attr("src", "static/images/icons/plus.png")
            .attr("title", "add model")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .on("click", async function () {
                obj.mu = null;
                await obj.update_view(this, false);
            });

        this.menu.append("img")
            .attr("id", "remove")
            .classed("view_menu_item", true)
            .attr("src", "static/images/icons/close.png")
            .attr("title", "remove model")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .on("click", async function () {
                if (obj.mu){ await models.remove(obj.mu); }
            });


        this.menu.append("img")
            .attr("id", "update")
            .classed("view_menu_item", true)
            .attr("src", "static/images/icons/update.png")
            .attr("title", "update all models")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .on("click", async function () {
                let shadow = d3.select("#wsg_drawing").append("rect").attr("id", "shadow")
                    .style("width", "100%").style("height", "100%")
                    .style("fill", "white").style("opacity", 0.5);
                await update_all_models();
                await post("update", {}, true);
                shadow.remove();
            });



        this.play = this.menu.append("img")
            .attr("id", "btn_play")
            .classed("view_menu_item", true)
            .attr("src","static/images/icons/Play.png")
            .attr("title", "start simulation")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .style("display", function () { return agent_data.active ? 'none' : 'block'})
            .on("click", async function() {
                await post("start", {},false);
                agent_data.status = "running";
                await obj.status();
            });

        this.pause = this.menu.append("img")
            .attr("id", "btn_pause")
            .classed("view_menu_item", true)
            .attr("src","static/images/icons/Pause.png")
            .attr("title", "pause simulation")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .style("display", function () { return agent_data.active ? 'block' : 'none'})
            .on("click", async function() {
                await post("pause", {},false);
                agent_data.status = "paused";
                await obj.status();
            });

        this.stop = this.menu.append("img")
            .attr("id", "btn_stop")
            .classed("view_menu_item", true)
            .attr("src","static/images/icons/Stop.png")
            .attr("title", "stop simulation")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .style("display", function () { return agent_data.active ? 'block' : 'none'})
            .on("click", async function() {
                await post("stop", {},false);
                agent_data.status = "stopped";
                await obj.status();
            });

        this.kill = this.menu.append("img")
            .attr("id", "btn_stop")
            .classed("view_menu_item", true)
            .attr("src","static/images/icons/cancel.png")
            .attr("title", "force stop simulation")
            .attr("width", icon_size)
            .attr("height", icon_size)
            .style("display", function () { return agent_data.active ? 'block' : 'none'})
            .on("click", async function() {
                await post("kill", {},false);
                agent_data.status = "stopped";
                await obj.status();
            });


        this.content = this.view.append('div')
            .attr('id', 'view_content');

        this.mu = null;
        this.set_mu(null);

        // Todo: delete this
        if (agent_data.active){
            agent_data.status = "running";
        } else {
            agent_data.status = "stopped";
        }
        obj.status();
    }

    async status(){
        switch(agent_data.status) {
            case 'running':
                this.play.style("display","none");
                this.pause.style("display","block");
                this.stop.style("display","block");
                this.kill.style("display","block");
                break;
            case 'paused':
                this.play.style("display","block");
                this.pause.style("display","none");
                this.stop.style("display","block");
                this.kill.style("display","block");
                break;
            case 'stopped':
                this.play.style("display","block");
                this.pause.style("display","none");
                this.stop.style("display","none");
                this.kill.style("display","none");
                break;
            default:
        }
    }

    async update_view(menu_item, new_mu){
        let obj = this;
        let mu = this.mu;
        clearInterval(this.update_interval);

        let menu_sel;
        if (menu_item){ // menu_item = X
            menu_sel = d3.select(menu_item)
        } else if (!mu){ // menu_item = null && mu = null
            menu_sel = this.menu.select("#add")
        } else  if (new_mu && this.menu.select("#add").classed("active")){ // menu_item = null && mu = X && new_mu = false
            menu_sel = this.menu.select("#docu");
        } else {
            menu_sel = this.menu.select(".active");
        }

        // update menu
        this.menu.selectAll(".view_menu_item").classed("active", false);
        menu_sel.classed("active", true);

        // update property & result menu item
        let items = ["properties", "results"];
        for (let i in items){
            let item = items[i];
            if (menu_sel.attr("id") === item && this.mu){
                log(item);
                log(menu_sel.attr("id") === item);
                if (this.mu.model.has_property_view){
                    if (!menu_sel.classed("custom") && menu_sel.classed("default")){
                        menu_sel.classed("custom", true);
                        menu_sel.classed("default", false);
                    } else {
                        menu_sel.classed("custom", false);
                        menu_sel.classed("default", true);
                    }
                } else {
                    menu_sel.classed("custom", false);
                    menu_sel.classed("default", false);
                }

            } else {
                this.menu.select("#"+item).classed("custom", false);
                this.menu.select("#"+item).classed("default", false);

            }
            this.menu.select("#"+item).html(function () {
                if ( obj.menu.select("#"+item).classed("custom")){return "default "+item}
                if ( obj.menu.select("#"+item).classed("default")){return "custom "+item}
                switch (item) {
                    case 'properties': return "Properties" ;
                    case 'results':return "Results";
                    default: return "";
                }
            });
        }




        // set title
        if (menu_sel.attr('id') === 'add'){ this.title.html("Add model"); }
        else if (mu){ this.title.html(`Model <b>${mu.name}</b> (${mu.model.topic}/${mu.model.name}/${mu.model.version})`); }
        else { this.title.html("no model selected" ); }

        // update view
        switch(menu_sel.attr('id')) {
            case 'add': await this.update_add_model(); break;
            case 'docu': await this.update_docu(); break;
            case 'properties':
                if (menu_sel.classed("custom")){ await this.update_custom_property_view(); }
                else { await this.update_default_property_view(); }
                break;
            case 'results':
                if (menu_sel.classed("custom")){ await this.update_custom_result_view(); }
                else { await this.update_default_result_view(); }
                break;
            default: this.content.html("");
        }
    }

    async set_mu(mu) {
        this.mu = mu;
        await this.update_view(null, true);
    }

    // methods to update view

    async update_docu() {
        this.content.html("");
        if (!this.mu) { return }
        let obj = this;
        let html = await get('get_model_readme', {'mu_id': obj.mu.id});
        this.content.html(html);
    }

    async update_default_result_view() {
        if (!this.mu) { this.content.html(""); return }
        this.run = 0;
        let obj = this;
        // speed
        this.content.html("");
        this.content.append("label").text("Update Speed [s]: ");
        this.content.append("input")
            .attr("type", "text")
            .attr("value", function () { return obj.interval_speed })
            .on('keyup', async function () {
                if (d3.event.keyCode === 13) {
                    obj.interval_speed = parseFloat(this.value);
                    await set_updater(obj)
                }
            })
            .on('blur', async function () {
                obj.interval_speed = parseFloat(this.value);
                await set_updater(obj)
            });
        this.content.append('label').classed("update_dot",true);
        this.content.append('br');
        this.content.append('br');
        await update(this);
        await set_updater(this);

        async function update(obj){
            let result = await get('get_mu_results', {'mu_id': obj.mu.id, 'mu_run': obj.run});
            result = JSON.parse(result);
            if (result){
                obj.run = result.run;

                result = obj.content.selectAll('.result').data(d3.entries(result.result));

                result.enter().append('div').classed('result', true);

                obj.content.selectAll('.result').html(function(res){
                    if (res.key === "time" || res.key === "times"){
                        if(Array.isArray(res.value)){
                            for (let i = 0; i < res.value.length; i++) {
                                res.value[i] = new Date(res.value[i]*1000).toString()
                            }
                        } else {
                            res.value = new Date(res.value*1000).toString()
                        }
                    }
                    return `<b>${res.key}:</b><br><div style="overflow-y: scroll; max-height:400px;"><pre>${JSON.stringify(res.value,null,5)}</pre></div>`
                });
            }
        }

        async function set_updater(obj) {
            clearInterval(obj.update_interval);
            obj.update_interval = setInterval(await async function() {
                obj.content.select(".update_dot").html("I");
                await update(obj);
                obj.content.select(".update_dot").html("");
            }, obj.interval_speed*1000);
        }
    }

    async update_custom_result_view(){
        if (!this.mu) { this.content.html(""); return }
        this.content.html("");
        let src = '/model_view?MU_id=' + this.mu.id + '&view=result';
        this.menu.select("#results").append("img")
            .attr("src", "static/images/icons/open.png")
            .style("width", "14px").style("height", "14px").style("margin-left", "15px")
            .on("click", function () {  window.open(src); });
        this.content.append("div").style("height", "500px").style("background-color","white")
            .html('<iframe src="' + src + '" width="100%" height="100%" ></iframe>');
    }

    async update_default_property_view() {
        if (!this.mu) { this.content.html(""); return }
        let obj = this;
        this.content.html("");

        let prop_data = await get('get_model_properties', {'model': obj.mu.id});
        prop_data = JSON.parse(prop_data);

        let form = this.content.selectAll(".propertiesForm").data([obj.mu]);
        form = form.enter().append("g").classed("properties", true).attr("name", "properties");

        let props = form.selectAll(".property")
            .data(function (mu) { return d3.entries(mu.model.info.properties) });
        props = props.enter().append("g").classed("property", true);
        props.append("span").html(function (d, i) {
            let brake = (i === 0 ? '' : '<br>');
            brake += (d.value.name + ' ['+ d.value.unit +']:<br>');

            return brake
        });
        props.append("input")
            .attr("id", function (d) { return d.key; })
            .attr("name", function (d) { return d.key; })
            .attr("type", "text")
            .attr("value", function (d) { return prop_data[d.key] })
            .on('keyup', function (d) {
                if (d3.event.keyCode === 13) {
                    post('set_model_property', {'model': obj.mu.id, 'property': d.key, 'value': this.value})
                }
            })
            .on('blur', function (d) {
                post('set_model_property', {'model': obj.mu.id, 'property': d.key, 'value': this.value})
            });
        props.append("br");
    }

    async update_custom_property_view() {
        if (!this.mu) { this.content.html(""); return }
        this.content.html("");
        let src = '/model_view?MU_id=' + this.mu.id + '&view=properties';
        this.menu.select("#properties").append("img")
            .attr("src", "static/images/icons/open.png")
            .style("width", "14px").style("height", "14px").style("margin-left", "15px")
            .on("click", function () { window.open(src); });
        this.content.append("div").style("height", "500px").style("background-color","white")
            .html('<iframe src="' + src + '" width="100%" height="100%" ></iframe>');
    }


    async update_add_model() {
        // Title
        this.content.html("");
        this.content.append("h2").text("Add Model");
        // Form
        let form = this.content.selectAll("form").data([all_models]).enter().append("from").attr("name", "addBoxForm");
        // Name
        form.append("span").html('Model Name:<br>');
        form.append("input")
            .attr("id", "model_name")
            .attr("name", "model_name")
            .attr("type", "text")
            .attr("value", "");
        // Topic
        form.append("span").html('<br>Topic:<br>');
        let t_sel = form.append("select").attr("id", "topic_selection").attr("name", "topic_selection")
            .on('change', function (d) {
                form.select("#model_selection").selectAll("option").remove();
                form.select("#model_selection").selectAll("option").data(d3.entries(d[this.value]))
                    .enter().append("option")
                    .attr("value", function (m) {return m.key})
                    .text(function (m) {return m.key});
                form.select("#model_selection").dispatch('change');
            });
        t_sel.selectAll(".topic_option").data(d3.entries(all_models))
            .enter().append("option")
            .attr("value", function (t) { return t.key })
            .text(function (t) { return t.key })
        // Model
        form.append("span").html('<br>Model:<br>');
        form.append("select").attr("id", "model_selection").attr("name", "model_selection")
            .on('change', function (d) {
                let t_val = t_sel.property("value");
                let vs = d[t_val][this.value];
                form.select("#version_selection").selectAll("option").remove();
                form.select("#version_selection").selectAll("option").data(d3.entries(vs))
                    .enter().append("option")
                    .attr("value", function (m) {return m.key})
                    .text(function (m) {return m.key});
                form.select("#version_selection").dispatch('change');
            });
        // Version
        form.append("span").html('<br>Version:<br>');
        form.append("select").attr("id", "version_selection").attr("name", "version_selection");
        form.append("span").html('<br>');
        form.append("input")
            .attr("type", "submit")
            .attr("value", "Submit")
            .on("click", async function () {
                let boxName = form.select("#model_name").property("value");
                if (boxName === "") {form.select("#model_name").style("background-color","red"); return}
                d3.select("#model_name").style("background-color","white");
                let v = form.select("#version_selection").property("selectedOptions")[0].__data__;
                await models.add(boxName, v.value.id);
                form.select("#model_name").node().value = "";
            });
        // trigger first change
        d3.select("#topic_selection").dispatch('change');
    }
}

