document.addEventListener('DOMContentLoaded', function () {
    highlightOwnedShifts();
});


function unassignedShiftClicked(day, shift) {
    let shiftDiv = document.getElementsByClassName('unscheduled-shift ' + day + '_' + shift)[0];
    shiftDiv.remove();
}

function existingShiftClicked(name, day, shift) {
    if(name == username){
        removeShift(name, day, shift);
        fillGaps();
    }else{
        alert("Nice try, bucko! You can only remove your own shifts.");
    }
}


function unassignedShiftClicked(day, shift){
    let shiftDiv = document.getElementsByClassName('unscheduled-shift '+day+'_'+shift)[0];
    shiftDiv.remove();
    let formatted_day = day.slice(0,3).toLowerCase();
    formatted_day = (formatted_day == 'thu') ? 'thur' : formatted_day;
    addShift(username,formatted_day,shift);
    window.location.reload()
}

function highlightOwnedShifts(){
    for(let day in schedule){
        for(let shift of schedule[day]){
            if(shift[1] == username){
                let shiftDiv = document.getElementById(day+'_'+shift[0]+'_'+shift[1]);
                shiftDiv.classList.add('red');
            }
        }
    }
}