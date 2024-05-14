let needed_shifts = JSON.parse(window.needed_shifts);
let avails = JSON.parse(window.avails);

//keeps track of all the shifts that are possible for each person on each day, inluding duplicates and checked shifts
let shifts = updateShifts(needed_shifts, avails);
let days = Object.keys(needed_shifts);
let names = Object.keys(avails);
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
    let startingAvail = avails[name][`${day}_start`];
    let endingAvail =  avails[name][`${day}_end`];
    
    return shift.startTime >= startingAvail && shift.endTime <= endingAvail;
}


function fillSchedule(schedule) {
    for (let day in schedule) {
        for (let name in schedule[day]) {
            console.log(schedule[day][name])
            for (let shift of schedule[day][name]) {
                checkShift(day, name, shift.shift);
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


//update availability based on the checked shifts
function getUpdatedAvails(avails_param) {
    let updatedAvails = JSON.parse(JSON.stringify(avails_param));
    for (let day of Object.keys(shifts)) {
        for (let name of names) {
            for (let shiftObj of shifts[day][name]) {
                if (isChecked(name, day, shiftObj.shift)) {

                    let sideOfDay = timeIsAMorPm(shiftObj.startTime);
                    if (sideOfDay == 'AM') {
                        updatedAvails[name][`${day}_start`] = shiftObj.endTime;
                    } else {
                        updatedAvails[name][`${day}_end`] = shiftObj.startTime;
                    }
                }
            }
        }
    }
    return updatedAvails;
}

//Get all the currently checked shifts as shiftObjs
function getCurrentFilledShifts() {
    let filled_shifts = {};
    let day_name_shiftobjs;
    for (let day of Object.keys(shifts)) {
        filled_shifts[day] = [];
        for (let name of names) {
            //Create a copy of shifts[day][name] that avoids duplicate shiftObjs
            day_name_shiftobjs = [];
            for (let shiftObj of shifts[day][name]) {
                if (isChecked(name, shiftObj.day, shiftObj.shift) && !day_name_shiftobjs.map(shift => shift.shift).includes(shiftObj.shift)) {
                    day_name_shiftobjs.push(shiftObj);
                }
            }
            filled_shifts[day] = filled_shifts[day].concat(day_name_shiftobjs);
        }
    }
    return filled_shifts;
}


function getCurrentlyNeededShifts() {
    let currentlyNeededShifts = {};
    let filled_shifts = getCurrentFilledShifts();
    for (let day of days) {
        currentlyNeededShifts[day] = getMissingShifts(filled_shifts[day], needed_shifts[day])
    }
    return currentlyNeededShifts;
}

function getShiftObjFromShiftName(day, shiftName, name) {
    return shifts[day][name].find(shift => shift.shift == shiftName);
}