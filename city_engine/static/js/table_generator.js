$(document).ready(function() {
    for(i = 0; i < 4; i++){
        if((i % 2) == 0){
            $('#table').append(hexRowEven)
            } else {
            $('#table').append(hexRow)
            }
        }
    for(i = 0; i < 4; i++){
        $('.hex-row').append(hex)
        $('.hex-row even').append(hex)
        }
    });

var hex = "<div class='hexagon'>" +
    "<div class='hexagon-top'></div>" +
    "<div class='hexagon-middle'></div>" +
    "<div class='hexagon-bottom'></div>" +
    "</div>"
var hexRow = "<div class='hex-row'></div>"
var hexRowEven =  "<div class='hex-row even'></div>"
