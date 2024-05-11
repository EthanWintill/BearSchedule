//import subtractArrays from utils.js
// import('./utils.js').then(utils => {
//     subtractArrays = utils.subtractArrays;
//     insertChildAlphabetically = utils.insertChildAlphabetically;
// })

let needed_shifts = JSON.parse(window.needed_shifts);
let schedule = JSON.parse(window.schedule);
let names = JSON.parse(window.names);
let username = JSON.parse(window.username);

document.addEventListener('DOMContentLoaded', function () {
    fillGaps();
});



//DOM manipulation
function AddUnassignedShift(day, shiftObj) {
    let shiftDiv = document.createElement('div');
    shiftDiv.classList.add('unscheduled-shift', shiftObj.day + '_' + shiftObj.shift);
    shiftDiv.innerHTML = shiftObj.shift + ': None';

    shiftDiv.setAttribute('onclick', 'unassignedShiftClicked(' + JSON.stringify(shiftObj) + ')');

    sideOfDay = timeIsAMorPm(shiftObj.startTime) 

    insertChildAlphabetically(document.getElementById(shiftObj.day + '_' + sideOfDay), shiftDiv);
}

//Database manipulation
function removeShift(name, day, shift) {
    //send a request to the server to remove the shift
    let week_offset = parseInt(window.location.href.split('/').pop()) // Nan if no route param
    fetch('/removeShift',
        {
            method: 'DELETE',
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
            alert('Beep Boop! Error removing shift. Try again.');
        });
}

function addShift(shiftObj, name) {
    //send a request to the server to add the shift
    let week_offset = parseInt(window.location.href.split('/').pop()) // Nan if no route param
    fetch('/addShift',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "name": name,
                "day": shiftObj.day,
                "shift": shiftObj.shift,
                "offset": week_offset? week_offset : 0,
                "shift_id": shiftObj.id
            }),
        })
}

//Other functions

function fillGaps() {
    for (let day in schedule) {
        let taken_shifts = schedule[day]//.map(shift => shift.shift) //TODO change this method to compare shift_ids
        formatted_day = day.slice(0, 3).toLowerCase();
        let missing_shifts = getMissingShifts(taken_shifts, needed_shifts[formatted_day])//.map(shift => shift.shift));
        //create a div with class 'unscheduled-shift day_shift' for each missing shift
        for (let shift of missing_shifts) {
            AddUnassignedShift(day,shift);
        }
    }
}

function getScheduleEntry(name, day, shift) {
    return schedule[day].find(entry => entry.name == name && entry.shift == shift);
}

function textSchedule(){
    fetch('/text-schedule',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
}