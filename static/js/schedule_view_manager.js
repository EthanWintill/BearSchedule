

function showDropdown(shiftObj) {
    let day = shiftObj.day;
    let shift = shiftObj.shift;
    let sideOfDay = timeIsAMorPm(shiftObj.startTime);
    let td = document.getElementById(day + '_' + sideOfDay);

    //create a dropdown with all the staff names
    let dropdown = document.createElement('select');
    dropdown.classList.add('staff-dropdown-shifts');
    dropdown.setAttribute('onchange', 'dropdownOptionSelected(' + JSON.stringify(shiftObj) + ',this.value)');
    //add options to the dropdown
    for (let name of names) {
        let option = document.createElement('option');
        option.value = name;
        option.text = name;
        dropdown.appendChild(option);
    }

    td.appendChild(dropdown);
}

//hide the dropdown
function hideDropdown(shiftObj) {
    let day = shiftObj.day;
    let sideOfDay = timeIsAMorPm(shiftObj.startTime);
    let td = document.getElementById(day + '_' + sideOfDay);
    let dropdown = td.getElementsByClassName('staff-dropdown-shifts')[0];
    dropdown.remove();
}

function unassignedShiftClicked(shiftObj) {
    let day = shiftObj.day;
    let shift = shiftObj.shift;
    showDropdown(shiftObj);
    let shiftDiv = document.getElementsByClassName('unscheduled-shift ' + day + '_' + shift)[0];
    shiftDiv.remove();
}

function dropdownOptionSelected(shiftObj, name) {
    addShift(shiftObj, name);
    hideDropdown(shiftObj);
}


function existingShiftClicked(name, day, shift) {
    removeShift(name, day, shift);
    fillGaps();
}

async function sendMassTextHTTP(message) {
    try {
        await fetch('/sendMassText', {
            method: 'POST',
            body: JSON.stringify({ message: message }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return true;
    } catch (error) {
        console.log(error);
        return false;
    }
}

async function sendMassText(message) {
    let element = document.getElementById('massTextDiv');
    let success = await sendMassTextHTTP(message);

    if (success) {
        element.style.border = 'solid 2px green';
        element.setAttribute('data-tooltip', 'Phone number successfully changed');
    } else {
        element.style.border = 'solid 2px red';
        element.setAttribute('data-tooltip', 'Error changing phone number');
    }

    setTimeout(() => {
        element.style.removeProperty('border');
        element.removeAttribute('data-tooltip');
    }, 5000);
}


function printSchedule() {
    let printFrame = document.createElement('iframe');
    printFrame.style.display = 'none';

    let schedule = document.getElementById('schedule-table');
    printFrame.srcdoc = '<html><head><title>Print</title>     <link rel="stylesheet" href="/static/css2/pico.min.css">   <link rel="stylesheet" href="/static/css/additions.css">    </head><body class="printScreen">' + schedule.outerHTML + '</body></html>';
    document.body.appendChild(printFrame);

    printFrame.contentWindow.focus();
    printFrame.contentWindow.print();
}