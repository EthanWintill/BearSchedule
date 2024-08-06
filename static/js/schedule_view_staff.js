document.addEventListener('DOMContentLoaded', function () {
     highlightOwnedShifts();
});



function existingShiftClicked(name, day, shift) {
    let shiftDiv = document.getElementById(day + '_' + shift + '_' + name);
    let shiftObj = getScheduleEntry(name, day, shift);
    if(name == username){
        let confirmDialog = !shiftDiv.classList.contains('isAvailable') ? 'Are you sure you would like to make this shift available to others?' : 'Are you sure you would like to make this shift as unavailable?';
        if(confirm(confirmDialog)){
            toggleShiftAvailabilityDB(shiftObj);
        }
    }else if(shiftDiv.classList.contains('isAvailable')){
        if(confirm('Are you sure you would like to claim this shift?')){
            sendShiftClaimRequest(username, shiftObj);
        }
    }else{
        alert("Nice try, bucko! You can only remove your own shifts.");
    }
}


function unassignedShiftClicked(shiftObj){
    let shiftDiv = document.getElementsByClassName('unscheduled-shift '+shiftObj.day+'_'+shiftObj.shift)[0];
    shiftDiv.remove();
    addShift(shiftObj,username);
    window.location.reload()
}

function highlightOwnedShifts(){
    for(let day in schedule){
        for(let shiftObj of schedule[day]){
            if(shiftObj.name == username){
                let shiftDiv = document.getElementById(day+'_'+shiftObj.shift+'_'+shiftObj.name);
                shiftDiv.classList.add('red');

                if(shiftObj.shift.slice(-1) == 'H'){
                    shiftDiv.classList.add('host');
                    shiftDiv.setAttribute('style', 'border: 1px solid #ffffff')
                }

                if(shiftDiv.classList.contains('isAvailable')){
                    shiftDiv.setAttribute( 'data-tooltip', 'This shift is available to others. Click to claim it.');
                }else{
                shiftDiv.setAttribute( 'data-tooltip', 'Click to make shift available');
                }
            }
        }
    }
}


function sendShiftClaimRequest(name, shiftObj){
    fetch('/shift_transfer_request',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "name": name,
                "shift_id": shiftObj.id
            }),
        }).then(response => {
            console.log(response);
        }).catch(error => {
            console.error('Error:', error);
            console.log(response.json());
            alert('Beep Boop! Error claiming shift. Try again.');
        }).then(() => {
            alert('Shift claim request sent!');
        });

}


function toggleShiftAvailabilityDB(shiftObj){
    fetch('/toggleShiftAvailability',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "shiftObj": shiftObj
            }),
        }).then(response => {
            console.log(response.json());
            window.location.reload();
        }).catch(error => {
            console.error('Error:', error);
            alert('Beep Boop! Error setting shift as available. Try again.');
        });
}

