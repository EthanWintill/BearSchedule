let needed_shifts = JSON.parse(window.needed_shifts);
let avails = JSON.parse(window.avails);
let shifts = updateShifts(needed_shifts,avails);
console.log(shifts);

document.addEventListener('DOMContentLoaded', function () {
    populateTable(shifts);
});


function populateTable(shifts){
    for(let day of Object.keys(shifts)){
        for(let person of Object.keys(shifts[day])){
            for(let shift of shifts[day][person]){
                addShiftOption(shift,person,day);
            }
        }
    }
}


function cancelForm(){
    window.location.href="/schedule_view"
}

function getPossibleShifts(name,day) {
    avail = avails[name][day];
    needed_shifts_day = needed_shifts[day];
    possibleShifts = [];
    for(let shift of needed_shifts_day){
        if (shift[0]=='5' && avail.includes('PM') || shift[0]!='5' && avail.includes('AM')) {
            possibleShifts.push(shift);
        }
    }
    return possibleShifts
}

function updateShifts(needed_shifts, avails){
    let shifts = {};
    for(let day of Object.keys(needed_shifts)){
        shifts[day] = {}
        for(let person of Object.keys(avails)){
            shifts[day][person] = getPossibleShifts(person,day);
        }
    }
    return shifts
}

function addShiftOption(shift, name, day) {
    let parent = document.getElementById(name+'_'+day);
    let option = document.createElement('option');
    option.value = shift;
    option.text = shift;
    try {
        parent.add(option);
    }catch{
        console.log('cant find element with id: '+ name+'_'+day);
    }
}

function deleteShiftOption(shift, name, day) {
    let parent = document.getElementById(`${name}_${day}`);
    let options = parent.getElementsByTagName('option');

    for (let i = 0; i < options.length; i++) {
        if (options[i].value === shift) {
            options[i].remove();
            break;
        }
    }
}


function updateDay(day, name){
    shift = document.getElementById(name+ '_' + day).value
    
}





