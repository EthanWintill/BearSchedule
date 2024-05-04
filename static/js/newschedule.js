


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

function addShiftOption(shift, name, day) {
    let parent;
    if (shift[0] == '5') {
        parent = document.getElementById(name + '_' + day + '_PM');
    } else {
        parent = document.getElementById(name + '_' + day + '_AM');
    }

    let checkbox = document.createElement('div');
    checkbox.setAttribute('onclick', "toggleCheckbox(this)")
    checkbox.setAttribute('class', `${name}_${day}_${shift} checkbox-div`);

    let hidden_check = document.createElement('input');
    hidden_check.type = 'checkbox';
    hidden_check.name = `${name}_${day}`;
    hidden_check.value = `${shift}`
    hidden_check.id = `${name}_${day}_${shift}_hiddencheck`;
    hidden_check.style.display = 'none';



    let label = document.createElement('label');
    label.appendChild(document.createTextNode(shift));

    checkbox.appendChild(hidden_check);
    checkbox.appendChild(label);
    insertChildAlphabetically(parent, checkbox);
}

function deleteShiftOption(shift, name, day) {
    const divs = document.getElementsByClassName(`${name}_${day}_${shift}`);
    // Loop through the divs
    for (let i = 0; i < divs.length; i++) {
        const div = divs[i];
        if (!div.classList.contains('checked')) {
            // Remove the div if no checked checkbox is found
            div.remove();
            // Exit the loop after removing the first matching div
            break;
        }
    }

}

function checkAvail(shift, name, day) {
    return avails[name][day].includes('AM') && shift[0] != '5' || avails[name][day].includes('PM') && shift[0] == '5'
}


function insertChildAlphabetically(parentElement, childElement) {
    const parentDiv = parentElement;
    const newDiv = childElement;

    // Find the correct position to insert the new div alphabetically based on classname
    const childClass = newDiv.className;
    let insertIndex = Array.from(parentDiv.children).findIndex(child => child.className > childClass);
    if (insertIndex === -1) {
        insertIndex = parentDiv.children.length; // Insert at the end if no greater value found
    }

    // Insert the new div at the correct position
    if (insertIndex === 0) {
        parentDiv.prepend(newDiv); // Insert at the beginning
    } else {
        parentDiv.children[insertIndex - 1].after(newDiv); // Insert after the element at insertIndex - 1
    }
}


function duplicateFilter() {

    for (let day of days) {
        for (let person of names) {
            for (let shift of shifts[day][person]) {
                shift_options = document.getElementsByClassName(person + '_' + day + '_' + shift);
                let show_index = 0;
                for (i = 0; i < shift_options.length; i++) {
                    if (shift_options[i].classList.contains('checked')) {
                        show_index = i;
                    }
                    shift_options[i].style.display = 'none';
                }
                shift_options[show_index].style.removeProperty('display');
            }
        }
    }
}

function checkShift(day, name, shift) {
    const shifts = document.getElementsByClassName(`${name}_${day}_${shift}`);
    toggleCheckbox(shifts[0])
}

function toggleCheckbox(element) {
    element.classList.toggle('checked');
    const [name, day, shift] = element.className.split(' ')[0].split('_');
    if (element.classList.contains('checked')) {
        console.log('Checkbox ' + element.className + ' is checked!');
        for (const person of names) {
            if (person == name) { continue; }
            index = shifts[day][person].indexOf(shift)
            if (index != -1) {
                shifts[day][person].splice(index, 1)
                deleteShiftOption(shift, person, day);
            }
        }
    } else {
        console.log('Checkbox is unchecked!');
        for (const person of names) {
            if (person == name) { continue; }
            if (checkAvail(shift, person, day)) {
                shifts[day][person].push(shift);
                addShiftOption(shift, person, day);
            }
        }
    }

    var hidden_check = element.querySelector('input[type="checkbox"]');
    hidden_check.checked = !hidden_check.checked;

    duplicateFilter();
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
            console.log('Optimal schedule received from the server bruh:', data);
            fillSchedule(data)
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Beep Boop! Error making schedule. Get more availability and try again.');
        });
}

function isChecked(name, day, shift){
    shiftContainer = document.getElementsByClassName(`${name}_${day}_${shift}`);
    for (let shiftDiv of shiftContainer){
        if(shiftDiv.classList.contains('checked')){
            return true;
        }
    }
    return false;
}

function getCurrentSchedule() {
    let schedule = {};
    for (let day of days) {
        schedule[day] = {};
        for (let name of names) {
            schedule[day][name] = [];
            for (let shift of shifts[day][name]) {
                if (document.getElementById(name + '_' + day + '_' + shift + '_hiddencheck').checked) {
                    schedule[day][name].push(shift);
                }
            }
        }
    }
    return schedule;
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

function subtractArrays(a, b) {
    // Create an object to store the count of each element in array a
    let countMap = {};
    a.forEach(element => {
        countMap[element] = (countMap[element] || 0) + 1;
    });

    // Iterate through array b and subtract elements from a
    let result = [];
    b.forEach(element => {
        if (countMap[element] && countMap[element] > 0) {
            countMap[element]--;
        } else {
            result.push(element);
        }
    });

    return result;
}


function getCurrentlyNeededShifts() {
    let currentlyNeededShifts = {};
    let filled_shifts = getCurrentFilledShifts();
    for (let day of days) {
        currentlyNeededShifts[day] = subtractArrays(filled_shifts[day], needed_shifts[day])
    }
    return currentlyNeededShifts;

}
function fillSchedule(schedule) {
    for (let day in schedule) {
        for (let name in schedule[day]) {
            console.log(schedule[day][name])
            for (let shift of schedule[day][name]) {
                console.log(day + shift + name);
                checkShift(day, name, shift);
            }
        }
    }

}

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

function autoCompleteSchedule() {
    let currentlyNeededShifts = getCurrentlyNeededShifts();
    let currentAvails = getUpdatedAvails(avails);
    computeSchedule(currentlyNeededShifts, currentAvails)
}
