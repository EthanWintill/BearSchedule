
function modifyRouteParam(amount) {
    let url = window.location.href
    let currentParam = parseInt(window.location.pathname.split('/').pop());

    if(isNaN(currentParam)){
        window.location.pathname += '/' +amount;
    }else{
        let newAmount = amount+currentParam
        window.location.href = url.slice(0,url.lastIndexOf('/')+1)+newAmount;
    }
}

function getOffset(){
    const offset = parseInt(window.location.pathname.split('/').pop());
    return isNaN(offset) ? 0 : offset;
}

function getWeekInt(){
    let offset = getOffset();
    return Math.floor((new Date).getTime() / (1000 * 60 * 60 * 24))-new Date().getDay()-1+offset*7;

}

function insertChildAlphabetically(parentElement, childElement) {
    const parentDiv = parentElement;
    const newDiv = childElement;

    // Find the correct position to insert the new div alphabetically based on classname
    const childClass = newDiv.className;
    let insertIndex = Array.from(parentDiv.children).findIndex(child => child.className > childClass);
    if (insertIndex === -1) {
        insertIndex = parentDiv.children.length; // Insert at the end if no greater value found
    }

    // Insert the new div at the correct position
    if (insertIndex === 0) {
        parentDiv.prepend(newDiv); // Insert at the beginning
    } else {
        parentDiv.children[insertIndex - 1].after(newDiv); // Insert after the element at insertIndex - 1
    }
}

function subtractArrays(small, big) {
    // Create an object to store the count of each element in array a
    let countMap = {};
    small.forEach(element => {
        countMap[element] = (countMap[element] || 0) + 1;
    });

    // Iterate through array b and subtract elements from a
    let result = [];
    big.forEach(element => {
        if (countMap[element] && countMap[element] > 0) {
            countMap[element]--;
        } else {
            result.push(element);
        }
    });

    return result;
}

function getMissingShifts(small, big) {
    // Create an object to store the count of each element in array a
    let countMap = {};
    small.forEach(element => {
        countMap[element.shift] = (countMap[element.shift] || 0) + 1;
    });

    // Iterate through array b and subtract elements from a
    let result = [];
    big.forEach(element => {
        if (countMap[element.shift] && countMap[element.shift] > 0) {
            countMap[element.shift]--;
        } else {
            result.push(element);
        }
    });

    return result;
}


function timeIsAMorPm(time) {
    return time<'14:30' ? 'AM' : 'PM';
}


function universal_toggle(checkDiv){
    if(checkDiv.classList.contains('checked')){
        checkDiv.classList.remove('checked');
    }else{
        checkDiv.classList.add('checked');
    }
}