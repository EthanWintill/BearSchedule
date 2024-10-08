let user_info = JSON.parse(window.user_info);

function toggleShiftCheck(element) {
    universal_toggle(element);
    let checkbox = element.querySelector('input');
    checkbox.toggleAttribute("checked");
}


function removeReqShift(day, shift) {
    fetch('/settings', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "day": day,
            "shift": shift
        })
    }).then(() => {
        setTimeout(() => {
            window.location.href = '/settings';
        }, 200);
    });
}

function toggleChangePassword() {
    let passDisplay = document.getElementById('disabledPasswordDiv');
    passDisplay.style.display = 'none';

    let passChange = document.getElementById('passwordDiv');
    passChange.style.removeProperty('display');
}

function toggleChangeUsername() {
    let usernameDisplay = document.getElementById('usernameDiv');
    if (usernameDisplay.style.display === 'none') {
        usernameDisplay.style.removeProperty('display');
    } else {
        usernameDisplay.style.display = 'none';
    }
}


function cancelPassChange() {
    let passDisplay = document.getElementById('disabledPasswordDiv');
    let passChange = document.getElementById('passwordDiv');

    passChange.style.display = 'none';
    passDisplay.style.removeProperty('display');
}

function confirmAccountDeletion(user_info, isManager) {
    if (isManager) {
        user_info = JSON.parse(user_info.replace(/'/g, '"')); // convert single quotes to double quotes 
    }
    let confirmDialog;
    if (isManager) {
        confirmDialog = 'Are you sure you want to delete ' + user_info['username'] + '\'s account? They will still appear on all schedules you are currently on, but will not be selectable for future schedules.';
    } else {
        confirmDialog = ('Are you sure you want to delete your account? You will still appear on all schedules you are currently on, but will not be selectable for future schedules.');
    }
    let confirmDelete = confirm(confirmDialog);

    if (!confirmDelete) { return; }

    fetch('/delete_account', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "user_id": user_info['id'],
            "is_manager": isManager
        })
    }).then(() => {
        if (isManager) {
            window.location.href = '/settings';
        } else {
            window.location.href = '/login';
        }
    }).catch((error) => {
        console.log(error);
    });
}

function sendPassChange(newPassword) {
    fetch('/change_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "new_password": newPassword,
            'user_id': user_info['id']
        })
    }).then(() => {
        cancelPassChange();
        alert('Password successfully changed');
    }).catch((error) => {
        console.log(error);
    });
}

function sendUsernameChange(newUsername) {
    fetch('/change_username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "new_username": newUsername,
            'user_id': user_info['id']
        })
    }).then(() => {
        alert('Username successfully changed');
        window.location.href = '/settings';
    }).catch((error) => {
        console.log(error);
    });
}

async function sendPhoneChange(newPhone, user_id) {
    try {
        await fetch('/change_phone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "new_phone": newPhone,
                'user_id': user_id
            })
        })
        return true;
    } catch (error) {
        console.log(error);
        return false;
    }
}

async function changeBorderColor(element) {
    let user_id = element.parentElement.parentElement.id;
    let success = await sendPhoneChange(element.value, user_id);

    if (success) {
        element.parentElement.style.border = 'solid 2px green';
        element.parentElement.setAttribute( 'data-tooltip', 'Phone number successfully changed');
    } else {
        element.parentElement.style.border = 'solid 2px red';
        element.parentElement.setAttribute( 'data-tooltip', 'Error changing phone number');
    }

    setTimeout(() => {
        element.parentElement.style.removeProperty('border');
        element.parentElement.removeAttribute('data-tooltip');
    }, 2000);
}