function keyGen(){
    var charSet = "01";
    var keyLength = 32;
    var key = "";
    for(var i = 0; i < keyLength; i++){
        key += charSet.charAt(Math.floor(Math.random()*charSet.length));
    }
    return key;
}

function indGen(){
    var tempInd = "";
    var charSet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    var indLength = 27;
    for(var i = 0; i < indLength; i++){
        tempInd += charSet.charAt(Math.floor(Math.random()*charSet.length));
    }
    return tempInd;
}

function stateGen(){
    var charSet = "01";
    var stateLength = 16;
    var state = "";
    for(var i = 0; i < stateLength; i++){
        state += charSet.charAt(Math.floor(Math.random()*charSet.length));
    }
    return state;
}