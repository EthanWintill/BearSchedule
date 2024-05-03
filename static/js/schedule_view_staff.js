document.addEventListener('DOMContentLoaded', function () {
     highlightOwnedShifts();
});



function existingShiftClicked(name, day, shift) {
    let shiftDiv = document.getElementById(day + '_' + shift + '_' + name);
    if(name == username){
        setShiftAsAvailable(day, shift, name);
    }else if(shiftDiv.classList.contains('isAvailable')){
        let formatted_day = day.slice(0,3).toLowerCase();
        formatted_day = (formatted_day == 'thu') ? 'thur' : formatted_day;
        removeShift(name, day.slice(0,3), shift);
        addShift(username,formatted_day,shift);
        window.location.reload();
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
                if(shiftDiv.classList.contains('isAvailable')){
                    shiftDiv.setAttribute( 'data-tooltip', 'This shift is available to others. Click to claim it.');
                }else{
                shiftDiv.setAttribute( 'data-tooltip', 'Click to make shift available');
                }
            }
        }
    }
}





function setShiftAsAvailable(day, shift, name){
    let week_offset = parseInt(window.location.href.split('/').pop()) // Nan if no route param
    fetch('/setShiftAsAvailable',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "name": name,
                "day": day.slice(0, 3).toLowerCase(),
                "shift": shift,
                "offset": week_offset? week_offset : 0
            }),
        }).then(response => {
            console.log(response.json());
            window.location.reload();
        }).catch(error => {
            console.error('Error:', error);
            alert('Beep Boop! Error setting shift as available. Try again.');
        });
}