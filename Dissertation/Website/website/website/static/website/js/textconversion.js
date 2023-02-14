function convertToBinary(string){
    result = "";
    for(var i = 0; i < string.length; i++){
        if(i == (string.length-1)){
            result += string[i].charCodeAt(0).toString(2)
        }
        else{
            result += string[i].charCodeAt(0).toString(2) + " ";
        }
    }
    return result;
}