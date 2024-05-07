let needed_shifts = JSON.parse(window.needed_shifts);
let avails = JSON.parse(window.avails);
let shifts = updateShifts(needed_shifts, avails);
let days = Object.keys(needed_shifts);
let names = Object.keys(avails);
let shiftTypes = ['10-3H', '12-5H', '10-4', '10-5', '5-10H', '5-CL']
console.log(shifts);

document.addEventListener('DOMContentLoaded', function () {
    populateTable(shifts);
    duplicateFilter();

});


function populateTable(shiftObjs) {
    for (let day of Object.keys(shiftObjs)) {
        for (let person of Object.keys(shiftObjs[day])) {
            for (let shiftObj of shiftObjs[day][person]) {
                addShiftOption(shiftObj, person, day);
            }
        }
    }
}


function cancelForm() {
    window.location.href = "/newschedule"
}

function getPossibleShifts(name, day) {
    avail = avails[name][day];
    needed_shifts_day = needed_shifts[day];
    possibleShifts = [];
    for (let shift of needed_shifts_day) {
        if (checkAvail(shift, name, day)) {
            possibleShifts.push(shift);
        }
    }
    return possibleShifts
}

function updateShifts(needed_shifts, avails) {
    let shifts = {};
    for (let day of Object.keys(needed_shifts)) {
        shifts[day] = {}
        for (let person of Object.keys(avails)) {
            shifts[day][person] = getPossibleShifts(person, day);
        }
    }
    return shifts
}



function checkAvail(shift, name, day) {
    day = day=='thu' ? 'thur' : day;

    let avail = avails[name][day];
    let startingAvail = '24:00';
    let endingAvail = '00:00';

    if (avail.includes('AM')) {
        startingAvail = '09:00';
        endingAvail = avail.includes('PM') ? '24:00' : '17:30';
    } else if (avail.includes('PM')) {
        startingAvail = '16:30';
        endingAvail = '24:00';
    }
    return shift.startTime >= startingAvail && shift.endTime <= endingAvail;
}


function fillSchedule(schedule) {
    for (let day in schedule) {
        for (let name in schedule[day]) {
            console.log(schedule[day][name])
            for (let shift of schedule[day][name]) {
                checkShift(day, name, shift);
            }
        }
    }

}

function autoCompleteSchedule() {
    let currentlyNeededShifts = getCurrentlyNeededShifts();
    let currentAvails = getUpdatedAvails(avails);
    computeSchedule(currentlyNeededShifts, currentAvails)
}





//Backend calls
function computeSchedule(shiftsNeeded, employeesAvailabilities) {
    fetch('/optimize-schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ shiftsNeeded, employeesAvailabilities }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Optimal schedule received from the server:', data);
            fillSchedule(data)
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Beep Boop! Error making schedule. Get more availability and try again.');
        });
}


//Get methods

function getUpdatedAvails(avails_param) {
    let updatedAvails = JSON.parse(JSON.stringify(avails_param));
    for (let day of days) {
        for (let name of names) {
            for (let shift of shiftTypes) {
                if(isChecked(name,day,shift)){

                    let isNightshift = shift[0] == '5';
                    if (isNightshift && updatedAvails[name][day].includes('PM')) {
                        updatedAvails[name][day] = updatedAvails[name][day].replace('PM', '');
                    }else if(updatedAvails[name][day].includes('AM')){
                        updatedAvails[name][day] = updatedAvails[name][day].replace('AM', '');
                    }

                }
            }
        }
    }
    return updatedAvails;
}


function getCurrentFilledShifts() {
    let filled_shifts = {};
    for (let day of days) {
        filled_shifts[day] = [];
        for (let name of names) {
            for (let shift of shiftTypes) {
                if (isChecked(name,day,shift)) {
                    filled_shifts[day].push(shift);
                }
            }
        }
    }
    return filled_shifts;
}


function getCurrentlyNeededShifts() {
    let currentlyNeededShifts = {};
    let filled_shifts = getCurrentFilledShifts();
    for (let day of days) {
        currentlyNeededShifts[day] = subtractArrays(filled_shifts[day], needed_shifts[day])
    }
    return currentlyNeededShifts;
}

function getShiftObjFromShiftName(day, shiftName, name){
    return shifts[day][name].find(shift => shift.shift == shiftName);
}