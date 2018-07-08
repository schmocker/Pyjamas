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

        let icon_size = 20;

        this.update_interval = null;
        this.interval_speed = 5;
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
                await post("update", {}, true);
                await obj.update_view();
                shadow.remove();
            });

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



        this.play = this.menu.append("img")
            .attr("id", "btn_play")
            .classed("view_menu_item", true)
            .attr("src","static/images/icons/Play.png")
            .attr("title", "start simulation")
            .attr("width", icon_size)
            .attr("height", icon_size)
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
            .on("click", async function() {
                await post("kill", {},false);
                agent_data.status = "stopped";
                await obj.status();
            });


        this.content = this.view.append('div')
            .attr('id', 'view_content');

        this.mu = null;
        this.m = null;
        this.set_mu(null);

        obj.status();
    }

    async status(){
        switch(agent_data.status) {
            case 'running':
                this.play.style("display","none");
                this.pause.style("display","block");
                this.stop.style("display","block");
                //this.kill.style("display","block");
                break;
            case 'paused':
                this.play.style("display","block");
                this.pause.style("display","none");
                this.stop.style("display","block");
                //this.kill.style("display","block");
                break;
            case 'stopped':
                this.play.style("display","block");
                this.pause.style("display","none");
                this.stop.style("display","none");
                //this.kill.style("display","none");
                break;
            default:
        }
    }

    async update_view(menu_item, new_mu){
        let obj = this;
        let mu = this.mu;
        let m = this.m;
        await this.status();
        clearInterval(this.update_interval);

        let menu_sel;
        if (menu_item){ // menu_item = X
            menu_sel = d3.select(menu_item)
        } else if (!mu){ // menu_item = null && mu = null
            menu_sel = this.menu.select("#add");
        } else  if (new_mu && this.menu.select("#add").classed("active")){ // menu_item = null && mu = X && new_mu = false
            menu_sel = this.menu.select("#properties");
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
            if (menu_sel.attr("id") === item && mu){
                log(item);
                log(menu_sel.attr("id") === item);

                let has = (item === "properties") ? "has_property_view" :  "has_result_view";

                if (m[has]){
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
        else if (mu){ this.title.html(`Model <b>${mu.name}</b> (${m.topic}/${m.name}/${m.version})`); }
        else { this.title.html("no model selected" ); }

        // update view
        switch(menu_sel.attr('id')) {
            case 'add':
                models.deactivate_all();
                await this.update_add_model();
                break;
            case 'docu':
                await this.update_docu();
                break;
            case 'properties':
                if (menu_sel.classed("custom")){ await this.update_custom_property_view(); }
                else { await this.update_default_property_view(); }
                break;
            case 'results':
                if (menu_sel.classed("custom")){ await this.update_custom_result_view(); }
                else { await this.update_default_result_view(); }
                break;
            default:
                this.content.html("");
        }
    }

    async set_mu(mu) {
        this.mu = mu;
        this.m = mu ? agent_data.models[mu.fk_model] : null;
        await this.update_view(null, true);
    }

    // methods to update view

    async update_docu() {
        this.content.html("");
        if (!this.mu) { return }
        let obj = this;
        let data = await get('get_model_readme', {'mu_id': obj.mu.id});
        this.content.html(data.html);
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


        let result_obj = obj.content.selectAll('.result').data(d3.entries(obj.m.outputs));
        let new_result_obj = result_obj.enter().append('div').classed('result', true);
        new_result_obj.append('b').text(function(d){return d.value.name + " [" + d.value.unit + "]" + ":";});
        new_result_obj.append('div').classed('value', true)
            .attr('style', 'overflow-y: scroll; max-height:200px;')
            .style('border', '1px solid');

        /*
        let result = await get('get_mu_results', {'mu_id': obj.mu.id, 'mu_run': obj.run});
        result = JSON.parse(result);
        let keys = Object.keys(result.result);
        let result_obj = obj.content.selectAll('.result').data(keys);
        let new_result_obj = result_obj.enter().append('div').classed('result', true);
        new_result_obj.append('b').text(function(d){return d + ":";});
        new_result_obj.append('div').classed('value', true)
            .attr('style', 'overflow-y: scroll; max-height:200px;')
            .style('border', '1px solid');
        */


        await update(this);
        await set_updater(this);

        async function update(obj){
            let result = await get('get_mu_results', {'mu_id': obj.mu.id, 'mu_run': obj.run});

            if (result){
                obj.content.selectAll('.value')
                    .html(function (d) {
                        let value = result.result[d.key];
                        if (d.key === "time" || d.key === "times"){
                            if(Array.isArray(value)){
                                for (let i = 0; i < value.length; i++) {
                                    value[i] = new Date(value[i]*1000).toString()
                                }
                            } else {
                                value = new Date(value*1000).toString()
                            }
                        }
                        return `<pre style="margin: 3px">${JSON.stringify(value,null,5)}</pre>`;
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
        let src = '/model_view?mu_id=' + this.mu.id + '&view=result';
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

        ////
        let data = [
            {'name': 'Properties',
                'columns': ['Name','Value','Unit','Info','Example'],
                'data': d3.entries(this.m.properties)},
            {'name': 'Inputs',
                'columns': ['Name','Unit','Info','Example'],
                'data': d3.values(this.m.inputs)},
            {'name': 'Outputs',
                'columns': ['Name','Unit','Info','Example'],
                'data': d3.values(this.m.outputs)},
            {'name': 'Settings',
                'columns': ['Name','Name Vertical Position','Name Horizontal Position','Inputs orientation','Outputs Orientation'],
                'data': [this.mu]}];

        this.content.append('div').attr('class','tab')
            .selectAll('.tablink').data(data).enter()
            .append('button').attr("class", "tablink")
            .text(function (d) { return d.name })
            .on('click', function (d) {
                obj.content.selectAll('.tablink').classed('active', false);
                d3.select(this).classed('active', true);
                obj.content.selectAll('.section').style('display', 'none');
                obj.content.select('.section#'+d.name).style('display', 'block');
            })
            .classed('active', function (d) { return (d.name==='Properties') });

        let sections = this.content.selectAll('.section').data(data)
            .enter().append('div').attr('class', 'section')
            .attr('id', function (d) { return d.name })
            .style('display', function (d) { return (d.name==='Properties') ? 'block' : 'none' });
        sections.filter(function (d) { return d.data.length === 0; }).append('p').text('none')
        let _table = sections.filter(function (d) { return d.data.length !== 0; }).append('table');
        let _thead = _table.append('thead');
        let	_tbody = _table.append('tbody');
        _thead.append('tr').selectAll('th').data(function (d) { return d.columns}).enter()
            .append('th').text(function (d) { return d; });
        let _tr = _tbody.selectAll("tr").data(function (d) { return d.data }).enter().append("tr");

        let tr_Properties = this.content.select('#Properties').select('tbody').selectAll('tr');
        let tr_InOutputs = this.content.selectAll('#Inputs, #Outputs').select('tbody').selectAll('tr');
        let tr_Settings = this.content.select('#Settings').select('tbody').selectAll('tr');

        fill_tr_Properties(tr_Properties);
        fill_tr_InOutputs(tr_InOutputs);
        fill_tr_Settings(tr_Settings);


        // funtions to fill tables
        function fill_tr_Properties(tr){
            tr.append('td').text(function (d) { return d.value.name });
            let prop_input = tr.append('td').append("input");
            tr.append('td').text(function (d) { return d.value.unit });
            tr.append('td').text(function (d) { return d.value.info });
            tr.append('td').text(function (d) { return d.value.example });
            prop_input.attr("id", function (d) { return d.key; })
                .attr("name", function (d) { return d.key; })
                .attr("type", "text")
                .attr("value", function (d) { return obj.mu.properties[d.key] })
                .on('keyup', async function (d) { if (d3.event.keyCode === 13) { await post_property(obj.mu.id, d.key, this.value) }})
                .on('blur', async function (d) { await post_property(obj.mu.id, d.key, this.value) });
            async function post_property(id, key, val) {
                await post('set_mu_property', {'mu_id': id, 'property': key, 'value': val});
            }
        }
        function fill_tr_InOutputs(tr){
            tr.append('td').text(function (d) { return d.name });
            tr.append('td').text(function (d) { return d.unit });
            tr.append('td').text(function (d) { return d.info });
            tr.append('td').text(function (d) { return d.example });
        }

        function fill_tr_Settings(tr){
            let settings = [
                {'class':'setting name','id':'name','type': 'input', 'default': obj.mu.name, 'mu_id': obj.mu.id},
                {'class':'setting name_pos','id':'vertical','type': 'select', 'default': obj.mu.name_v_position,
                    'mu_id': obj.mu.id,'options':['top outside', 'top inside', 'center', 'bottom inside', 'bottom outside']},
                {'class':'setting name_pos','id':'horizontal','type': 'select', 'default': obj.mu.name_h_position,
                    'mu_id': obj.mu.id, 'options':['left outside', 'left inside', 'center', 'right inside', 'right outside']},
                {'class':'setting _orientation','id':'input_o','type': 'select', 'default': obj.mu.input_orientation,
                    'mu_id': obj.mu.id, 'options':['top','bottom','left','right'], 'dock': 'input'},
                {'class':'setting _orientation','id':'output_o','type': 'select', 'default': obj.mu.output_orientation,
                    'mu_id': obj.mu.id, 'options':['top','bottom','left','right'], 'dock': 'output'}];

            let tds = tr.selectAll('.setting').data(settings).enter().append('td');
            tds.append(function (d) { return document.createElement(d.type) })
                .attr('id', function (d) { return d.id  }).attr('class', function (d) { return d.class  });

            tds.select('#name')
                .attr("type", "text").attr("value", function (d) { return d.default })
                .on('keyup', async function (d) {
                    obj.title.select('b').property('textContent', this.value);
                    main.select('#mu_'+d.mu_id).select(".model_name").text(this.value);
                    if (d3.event.keyCode === 13) { await post_model_name(d.mu_id, this.value) }
                })
                .on('blur', async function (d) { await post_model_name(d.mu_id, this.value) });
            async function post_model_name(id, val) {
                await post('set_mu_name', {'mu_id': id, 'name': val}, true);
            }

            tds.selectAll('.name_pos')
                .on('change', async function (d) {
                    await post('set_mu_name_pos',
                        {'mu_id': d.mu_id, 'axis': d.id, 'position': this.value},
                        true);
                });

            tds.selectAll('._orientation')
                .on('change', async function (d) {
                    if (tr.select('#input_o').property('value') === tr.select('#output_o').property('value')){
                        d3.select(this).style('background-color', 'red');
                    } else {
                        d3.select(this).style('background-color', 'white');
                        await post('set_mu_dock_orientation',
                            {'mu_id': obj.mu.id, 'dock': d.dock, 'orientation': this.value},
                            true);
                    }
                });
            tds.selectAll('select').selectAll('option').data(function (d) { return d.options })
                .enter().append('option')
                .attr("value", function (d) { return d })
                .text(function (d) { return d });
            tds.selectAll('select').property('value',function (d) { return d.default  });
        }
    }

    async update_custom_property_view() {
        if (!this.mu) { this.content.html(""); return }
        this.content.html("");
        let src = '/model_view?mu_id=' + this.mu.id + '&view=properties';
        this.menu.select("#properties").append("img")
            .attr("src", "static/images/icons/open.png")
            .style("width", "14px").style("height", "14px").style("margin-left", "15px")
            .on("click", function () { window.open(src); });
        this.content.append("div").style("height", "500px").style("background-color","white")
            .html('<iframe src="' + src + '" width="100%" height="100%" ></iframe>');
    }


    async update_add_model() {
        let all_models = {};
        for (let id in agent_data.models){
            let model = agent_data.models[id];

            let t = model.topic;
            let n = model.name;
            let v = model.version;

            if (!(t in all_models)){ all_models[t] = {} }
            if (!(n in all_models[t])){ all_models[t][n] = {} }

            all_models[t][n][v] = model.id;
        }

        all_models = sort_dict(all_models);

        function sort_dict(dict){
            let new_dict = {};
            let sorted_key = Object.keys(dict).sort();
            for (let i in sorted_key){
                let key = sorted_key[i];
                let value = dict[key];
                new_dict[key] = (typeof value === typeof {}) ? sort_dict(value) : value
            }
            return new_dict;
        }

        let obj = this;
        // Title
        this.content.html("");
        this.content.append("h2").text("Add Model");
        // Form
        let form = this.content.selectAll("form").data([all_models]).enter().append("from").attr("name", "addBoxForm");
        // Name
        form.append("span").html('Model Name:<br>');
        let name_inp = form.append("input")
            .attr("id", "model_name")
            .attr("name", "model_name")
            .attr("type", "text")
            .attr("value", "");
        // Topic
        form.append("span").html('<br>Topic:<br>');
        let t_sel = form.append("select").attr("id", "topic_selection").attr("name", "topic_selection")
            .on('change', function (d) {
                m_sel.selectAll("option").remove();
                m_sel.selectAll("option").data(d3.entries(d[this.value]))
                    .enter().append("option")
                    .attr("value", function (m) {return m.key})
                    .text(function (m) {return m.key});
                m_sel.dispatch('change');
            });
        t_sel.selectAll(".topic_option").data(d3.entries(all_models))
            .enter().append("option")
            .attr("value", function (t) { return t.key })
            .text(function (t) { return t.key })
        // Model
        let m_sel_value;
        form.append("span").html('<br>Model:<br>');
        let m_sel = form.append("select").attr("id", "model_selection").attr("name", "model_selection")
            .on('change', function (d) {
                let name_value = name_inp.property("value");
                let changeName = (name_value === m_sel_value || name_value === "");
                m_sel_value = m_sel.property("value");
                if(changeName){ name_inp.property("value", m_sel_value); }

                let t_val = t_sel.property("value");
                let vs = d[t_val][this.value];
                v_sel.selectAll("option").remove();
                v_sel.selectAll("option").data(d3.entries(vs))
                    .enter().append("option")
                    .attr("value", function (m) {return m.key})
                    .text(function (m) {return m.key});
                v_sel.dispatch('change');
            });

        // Version
        form.append("span").html('<br>Version:<br>');
        let v_sel = form.append("select").attr("id", "version_selection").attr("name", "version_selection");

        // submit
        form.append("span").html('<br>');
        form.append("input")
            .attr("type", "submit")
            .attr("value", "Add")
            .on("click", async function () {
                let name = name_inp.property("value");
                if (name === "") {name_inp.style("background-color","red"); return; }
                name_inp.style("background-color","white");
                let v = v_sel.property("selectedOptions")[0].__data__;
                await models.add(name, v.value);

                let ids = Object.keys(agent_data.model_used);
                for(let i=0; i<ids.length;i++) ids[i] = parseInt(ids[i]);
                models.activate(Math.max(...ids));
            });
        // trigger first change
        t_sel.dispatch('change');
    }
}

