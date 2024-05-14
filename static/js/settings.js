function toggleShiftCheck(element){
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
