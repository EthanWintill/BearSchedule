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
function cancelPassChange() {
    let passDisplay = document.getElementById('disabledPasswordDiv');
    let passChange = document.getElementById('passwordDiv');

    passChange.style.display = 'none';
    passDisplay.style.removeProperty('display');
}

function confirmAccountDeletion(user_info, isManager) {
    if (isManager){
        user_info = JSON.parse(user_info.replace(/'/g, '"')); // convert single quotes to double quotes 
    }
    let confirmDialog;
    if (isManager) {
        confirmDialog = 'Are you sure you want to delete ' + user_info['username'] + '\'s account? They will still appear on all schedules you are currently on, but will not be selectable for future schedules.';
    } else {
        confirmDialog = ('Are you sure you want to delete your account? You will still appear on all schedules you are currently on, but will not be selectable for future schedules.');
    }
    let confirmDelete = confirm(confirmDialog);

    if (!confirmDelete){return;}

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
        }else{
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