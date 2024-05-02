function removeShift(name, day, shift){
    //send a request to the server to remove the shift
    fetch('/removeShift', 
    {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "name" : name, 
            "day": day, 
            "shift": shift
        }),
    }).then(response => {
        console.log(response.json());
        window.location.reload();
    }).catch(error => {
        console.error('Error:', error);
        alert('Beep Boop! Error removing shift. Try again.');
    });
}

function addShift(name, day, shift){
    //send a request to the server to add the shift
    fetch('/addShift', 
    {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "name" : name, 
            "day": day, 
            "shift": shift
        }),
    })
}