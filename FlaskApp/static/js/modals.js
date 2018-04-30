var modal = document.getElementById('myModal');

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];



// When the user clicks the button, open the modal
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks on submit , close the modal and add box
function validateForm() {
    var boxName = document.forms["addBoxForm"]["boxName"].value;
    if (boxName == "") {
        alert("Box Name must be filled out");
        return false;
    }
    modal.style.display = "none";
    boxes.push(new Box(boxName,'working_field'));
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
