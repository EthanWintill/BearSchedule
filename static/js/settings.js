


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
            window.location.reload();
        }, 200);
    });
}

function addReqShift(day, shift) {
    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "day": day,
            "shift": shift
        })
    }).then(() => {
        setTimeout(() => {
            window.location.reload();
        }, 200);
    });
}