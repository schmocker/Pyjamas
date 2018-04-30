var modal;
var btn;
var span;
var websimgui;


window.onload = function() {
    websimgui = new WebSimGui();


    modal = document.getElementById('myModal');
    btn = document.getElementById("myBtn");
    span = document.getElementsByClassName("close")[0];
    btn.onclick = function() {
        modal.style.display = "block";
    }
    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    agent = JSON.parse(agent_data);
    for (var model_id in agent){
        websimgui.addBox(model_id,agent[model_id]);
    }




}



class WebSimGui {
    constructor(){

        this.svgContainer = d3.select("#working_field").append("svg")
            .attr("width", "100%")
            .attr("height", "100%");
        this.boxes = {};
        this.connections = Array();
    }

    addBox(id, data){
        this.boxes[id] = new Box(this, id,data);
    }

    addConnection(box1, box2){
        this.connections.push(new Connection(box1,box2,this.svgContainer));
    }
}



function validateForm() {
    var boxName = document.forms["addBoxForm"]["boxName"].value;
    if (boxName == "") {
        alert("Box Name must be filled out");
        return false;
    }
    modal.style.display = "none";
    websimgui.addBox(boxName);
}


d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
  this.parentNode.appendChild(this);
  });
};
