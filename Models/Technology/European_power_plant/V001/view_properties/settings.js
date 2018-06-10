class Settings {
    constructor(){
        this.pp = null;
        this.PP = powerplants;
    }

    async build() {
        let obj = this;

        this.body = d3.select("#settings");

        this.body.append("img")
            .attr("id", "btn_add_pp")
            .attr("src","static/images/icons/plus.png")
            .on("click", async function() {
                await powerplants.addPP();
            });
        this.body.append("br");


        this.body.append("span").html('Name:');
        this.body.append("input")
            .attr("id",'name')
            .classed("input", true)
            .attr("name",'name')
            .attr("type","text");
        this.body.append("br");


        this.body.append("span").html('Latitude:');
        this.body.append("input")
            .attr("id",'lat')
            .classed("input", true)
            .attr("name",'lat')
            .attr("type","text")
            .on("input", async function(d) {
                let nums = this.value.match(/[\d]*[.]?[\d]*/g);
                for (let i = 1; i < nums.length; i++) { nums[i] = nums[i].replace(/[.]?/g, ''); }
                this.value = nums.join('');
                obj.PP.lat = this.value;
            })
            .on('blur', async function (d) {
                await powerplants.sendPP();
                await obj.update();
            });
        this.body.append("br");


        this.body.append("span").html('Longitude:');
        this.body.append("input")
            .attr("id",'lon')
            .classed("input", true)
            .attr("name",'lon')
            .attr("type","text")
            .on("input", async function(d) {
                let nums = this.value.match(/[\d]*[.]?[\d]*/g);
                for (let i = 1; i < nums.length; i++) { nums[i] = nums[i].replace(/[.]?/g, ''); }
                this.value = nums.join('');
                obj.PP.lon = this.value;
            })
            .on('blur', async function (d) {
                await powerplants.sendPP();
                await obj.update();
            });
        this.body.append("br");


        this.body.append("button")
            .attr("id",'delete')
            .classed("button", true)
            .text("delete item")
            .on('click', async function (d) {
                if (this.index > -1) {
                    await this.PP.delete_active();
                }
            });

        await this.update();
    }



    async update(){
        settings.body.select('#name').node().value = this.PP.name;
        settings.body.select('#lat').node().value = (this.PP.lat==="") ? "" : parseFloat(this.PP.lat).toFixed(6);
        settings.body.select('#lon').node().value = (this.PP.lon==="") ? "" : parseFloat(this.PP.lon).toFixed(6);
    }
}