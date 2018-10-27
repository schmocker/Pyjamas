import { WebSimGui } from "./js/WebSimGui.js";

let wsg;

window.onload = async function() {
    wsg = new WebSimGui("#wsg");
    wsg.start();
};

