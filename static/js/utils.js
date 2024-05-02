
function modifyRouteParam(amount) {
    url = window.location.href
    currentParam = parseInt(window.location.pathname.split('/').pop());

    if(isNaN(currentParam)){
        window.location.pathname += '/' +amount;
    }else{
        newAmount = amount+currentParam
        window.location.href = url.slice(0,url.lastIndexOf('/')+1)+newAmount;
;
    }
}