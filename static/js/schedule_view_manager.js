

function showDropdown(day,shift){
    let formatted_day = day.slice(0,3).toLowerCase();
    formatted_day = (formatted_day == 'thu') ? 'thur' : formatted_day;
    let sideOfDay = shift[0]=='5'? 'PM':'AM';
    let td = document.getElementById(day+'_'+sideOfDay);

    //create a dropdown with all the staff names
    let dropdown = document.createElement('select');
    dropdown.classList.add('staff-dropdown-shifts');
    dropdown.setAttribute('onchange', 'dropdownOptionSelected("'+formatted_day+'","'+shift+'",this.value)'); 
    //add options to the dropdown
    for(let name of names){
        let option = document.createElement('option');
        option.value = name;
        option.text = name;
        dropdown.appendChild(option);
    }

    td.appendChild(dropdown);
}

function unassignedShiftClicked(day, shift){
    showDropdown(day,shift);
    let shiftDiv = document.getElementsByClassName('unscheduled-shift '+day+'_'+shift)[0];
    shiftDiv.remove();
}

function dropdownOptionSelected(day,shift,name){
    addShift(name,day,shift)
    window.location.reload()
}


function existingShiftClicked(name, day, shift) {
    removeShift(name, day, shift);
    fillGaps();
}