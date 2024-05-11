


function cancelForm(){
    window.location.href = "/schedule_view";
}


function customAvailability(event){

    event.preventDefault();

    var form = event.target;

    // Get the values from the form
    var startTime = form.elements['start'].value;
    var endTime = form.elements['end'].value;
    var day = form.elements['day'].value;


    let amCheck = document.getElementById(`${day}-av-AM`);
    let pmCheck = document.getElementById(`${day}-av-PM`);
    console.log(amCheck, pmCheck);

    amCheck.setAttribute("value", startTime);
    amCheck.checked = true;
    amCheck.innerHTML = 'From: ' + startTime

    pmCheck.setAttribute("value", endTime);
    pmCheck.checked = true;
    pmCheck.innerHTML = 'To: ' + endTime
}

// form.addEventListener("submit", (event) => {
//     console.log("Form submitted!");
//     customAvailability(event);
// });
  

function checkBoth(day){
    let amCheck = document.getElementById(`${day}-av-AM`);
    let pmCheck = document.getElementById(`${day}-av-PM`);
    amCheck.toggleAttribute("checked");
    pmCheck.toggleAttribute("checked");
}