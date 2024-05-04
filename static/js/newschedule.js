let needed_shifts = JSON.parse(window.needed_shifts);
let avails = JSON.parse(window.avails);
let shifts = updateShifts(needed_shifts, avails);
console.log(shifts);

document.addEventListener('DOMContentLoaded', function () {
    populateTable(shifts);
});


function populateTable(shifts) {
    for (let day of Object.keys(shifts)) {
        for (let person of Object.keys(shifts[day])) {
            for (let shift of shifts[day][person]) {
                addShiftOption(shift, person, day);
            }
        }
    }
}


function cancelForm() {
    window.location.href = "/schedule_view"
}

function getPossibleShifts(name, day) {
    avail = avails[name][day];
    needed_shifts_day = needed_shifts[day];
    possibleShifts = [];
    for (let shift of needed_shifts_day) {
        if (checkAvail(shift,name,day)) {
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

function addShiftOption(shift, name, day) {
    let parent = document.getElementById(name + '_' + day);
    let checkbox = document.createElement('input');
    let div = document.createElement('div');
    div.setAttribute('class', `${name}_${day}_${shift}_div`);
    checkbox.type = 'checkbox';
    checkbox.name = `${name}_${day}`;
    checkbox.value = `${shift}`
    checkbox.id = `${name}_${day}_${shift}`;
    checkbox.class = 'container';
    checkbox.setAttribute('onchange', `handleCheckboxChange(this)`);
    let label = document.createElement('label');
    label.htmlFor = `${name}_${day}_${shift}`;
    label.appendChild(document.createTextNode(shift));

    div.appendChild(checkbox);
    div.appendChild(label);
    parent.appendChild(div);
}

function deleteShiftOption(shift, name, day) {
    const divs = document.getElementsByClassName(`${name}_${day}_${shift}_div`);

    // Loop through the divs
    for (let i = 0; i < divs.length; i++) {
        const div = divs[i];

        // Check if the div does not contain a checkbox that is checked
        const checkbox = div.querySelector('input[type="checkbox"]:checked');

        if (!checkbox) {
            // Remove the div if no checked checkbox is found
            div.remove();

            // Exit the loop after removing the first matching div
            break;
        }
    }

}

function handleCheckboxChange(checkbox) {
    const [name, day, shift] = checkbox.id.split('_');
    if (checkbox.checked) {
        console.log('Checkbox ' + checkbox.id + ' is checked!');
        for (const person of Object.keys(shifts[day])) {
            if (person == name) { continue; }
            index = shifts[day][person].indexOf(shift)
            if (index != -1) {
                shifts[day][person].splice(index, 1)
                deleteShiftOption(shift, person, day);
            }
        }
    } else {
        console.log('Checkbox is unchecked!');
        for (const person of Object.keys(shifts[day])) {
            if (person == name) { continue; }
            if (checkAvail(shift, person, day)) {
                shifts[day][person].push(shift);
                addShiftOption(shift, person, day);
            }
        }
    }

}

function checkAvail(shift, name, day) {
    return avails[name][day].includes('AM') && shift[0] != '5' || avails[name][day].includes('PM') && shift[0] == '5'
}

function updateDay(day, name) {
    shift = document.getElementById(name + '_' + day).value

}

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
    })
    .catch(error => {
        console.error('Error:', error);
    });

}


