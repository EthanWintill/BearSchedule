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
function AddUnassignedShift(day, shift) {
    let shiftDiv = document.createElement('div');
    shiftDiv.classList.add('unscheduled-shift', day + '_' + shift);
    shiftDiv.innerHTML = shift + ': None';

    shiftDiv.setAttribute('onclick', 'unassignedShiftClicked("' + day + '","' + shift + '")');

    sideOfDay = shift[0]=='5'? 'PM':'AM';

    insertChildAlphabetically(document.getElementById(day + '_' + sideOfDay), shiftDiv);
}

//Database manipulation
function removeShift(name, day, shift) {
    //send a request to the server to remove the shift
    fetch('/removeShift',
        {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "name": name,
                "day": day,
                "shift": shift
            }),
        }).then(response => {
            console.log(response.json());
            window.location.reload();
        }).catch(error => {
            console.error('Error:', error);
            alert('Beep Boop! Error removing shift. Try again.');
        });
}

function addShift(name, day, shift) {
    //send a request to the server to add the shift
    fetch('/addShift',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "name": name,
                "day": day,
                "shift": shift
            }),
        })
}

//Other functions

function fillGaps() {
    for (let day in schedule) {
        let taken_shifts = schedule[day].map(shift => shift[0])
        formatted_day = day.slice(0, 3).toLowerCase();
        formatted_day = (formatted_day == 'thu') ? 'thur' : formatted_day;
        let missing_shifts = subtractArrays(taken_shifts, needed_shifts[formatted_day]);
        //create a div with class 'unscheduled-shift day_shift' for each missing shift
        for (let shift of missing_shifts) {
            AddUnassignedShift(day, shift);
        }
    }
}
