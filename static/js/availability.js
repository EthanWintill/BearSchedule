document.addEventListener('DOMContentLoaded', function () {
    let days_of_week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
})


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


    toggleCheck(day, 'AM');
    toggleCheck(day, 'PM');

    let amCheck = document.getElementById(`${day}-av-AM`);
    let pmCheck = document.getElementById(`${day}-av-PM`);

    let amCheckLabel = document.getElementById(`${day}-label-AM`);
    let pmCheckLabel = document.getElementById(`${day}-label-PM`);

    amCheck.setAttribute("value", startTime);

    startTime = new Date(`1970-01-01T${startTime}:00`);
    startTime = startTime.toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'});
    amCheckLabel.innerHTML = startTime;

    pmCheck.setAttribute("value", endTime);

    endTime = new Date(`1970-01-01T${endTime}:00`);
    endTime = endTime.toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'});
    pmCheckLabel.innerHTML = '' + endTime

    document.querySelector('dialog').open = false;
}


  

function checkBoth(day){
    toggleCheck(day, 'AM');
    toggleCheck(day, 'PM');
}


function toggleCheck(day, AmOrPm){
    let check = document.getElementById(`${day}-av-${AmOrPm}`);
    check.toggleAttribute("checked");

    let checkDiv = document.getElementById(`${day}-div-${AmOrPm}`);
    if(checkDiv.classList.contains('checked')){
        checkDiv.classList.remove('checked');
    }else{
        checkDiv.classList.add('checked');
    }
}