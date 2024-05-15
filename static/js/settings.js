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