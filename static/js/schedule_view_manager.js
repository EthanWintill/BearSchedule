

function showDropdown(shiftObj){
    let day = shiftObj.day;
    let shift = shiftObj.shift;
    let sideOfDay = timeIsAMorPm(shiftObj.startTime);
    let td = document.getElementById(day+'_'+sideOfDay);

    //create a dropdown with all the staff names
    let dropdown = document.createElement('select');
    dropdown.classList.add('staff-dropdown-shifts');
    dropdown.setAttribute('onchange', 'dropdownOptionSelected('+ JSON.stringify(shiftObj) +',this.value)'); 
    //add options to the dropdown
    for(let name of names){
        let option = document.createElement('option');
        option.value = name;
        option.text = name;
        dropdown.appendChild(option);
    }

    td.appendChild(dropdown);
}

function unassignedShiftClicked(shiftObj){
    let day = shiftObj.day;
    let shift = shiftObj.shift;
    showDropdown(shiftObj);
    let shiftDiv = document.getElementsByClassName('unscheduled-shift '+day+'_'+shift)[0];
    shiftDiv.remove();
}

function dropdownOptionSelected(shiftObj,name){
    addShift(shiftObj, name)
    window.location.reload()
}


function existingShiftClicked(name, day, shift) {
    removeShift(name, day, shift);
    fillGaps();
}