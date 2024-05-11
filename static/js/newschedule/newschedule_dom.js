function addShiftOption(shiftObj, name, day) {
    const sideOfDay = timeIsAMorPm(shiftObj.startTime);
    let parent = document.getElementById(name + '_' + day + '_' + sideOfDay);

    let checkbox = document.createElement('div');
    checkbox.setAttribute('onclick', "toggleCheckbox(this)")
    checkbox.setAttribute('class', `${name}_${day}_${shiftObj.shift} checkbox-div`);

    let hidden_check = document.createElement('input');
    hidden_check.type = 'checkbox';
    hidden_check.name = `${name}_${day}`;
    hidden_check.value = `${shiftObj.id}`
    hidden_check.id = `${name}_${day}_${shiftObj.shift}_hiddencheck`;
    hidden_check.style.display = 'none';



    let label = document.createElement('label');
    label.appendChild(document.createTextNode(shiftObj.shift));

    checkbox.appendChild(hidden_check);
    checkbox.appendChild(label);
    insertChildAlphabetically(parent, checkbox);
}


function deleteShiftOption(shiftObj, name, day) {
    shift = shiftObj.shift;
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

function toggleCheckbox(element) {
    element.classList.toggle('checked');
    const [name, day, shiftName] = element.className.split(' ')[0].split('_');
    let shiftObj = getShiftObjFromShiftName(day, shiftName, name);
    if (element.classList.contains('checked')) {
        console.log('Checkbox ' + element.className + ' is checked!');
        for (const person of names) {
            if (person == name) { continue; }
            index = shifts[day][person].map(shift => shift.shift).indexOf(shiftName)
            if (index != -1) {
                deleteShiftOption(shiftObj, person, day);
                shifts[day][person].splice(index, 1)
            }
        }
    } else {
        console.log('Checkbox is unchecked!');
        for (const person of names) {
            if (person == name) { continue; }
            if (checkAvail(shiftObj, person, day)) {
                shifts[day][person].push(shiftObj);
                addShiftOption(shiftObj, person, day);
            }
        }
    }

    var hidden_check = element.querySelector('input[type="checkbox"]');
    hidden_check.checked = !hidden_check.checked;

    duplicateFilter();
}


function duplicateFilter() {

    for (let day of days) {
        for (let person of names) {
            for (let shiftObj of shifts[day][person]) {
                shift_options = document.getElementsByClassName(person + '_' + day + '_' + shiftObj.shift);
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

function checkShift(day, name, shiftName) {
    const shifts = document.getElementsByClassName(`${name}_${day}_${shiftName}`);
    toggleCheckbox(shifts[0])
}


//DOM manipulation -- Get methods
function getCurrentSchedule() {
    let schedule = {};
    for (let day of days) {
        schedule[day] = {};
        for (let name of names) {
            schedule[day][name] = [];
            for (let shiftObj of shifts[day][name]) {
                if (document.getElementById(name + '_' + day + '_' + shiftObj.shift + '_hiddencheck').checked) {
                    schedule[day][name].push(shiftObj.shift);
                }
            }
        }
    }
    return schedule;
}

function isChecked(name, day, shiftName){
    shiftContainer = document.getElementsByClassName(`${name}_${day}_${shiftName}`);
    for (let shiftDiv of shiftContainer){
        if(shiftDiv.classList.contains('checked')){
            return true;
        }
    }
    return false;
}
