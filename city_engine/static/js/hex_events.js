$(document).ready(function() {
    $('.buildingsToBuild').hide();

    $('.hex-change').click(function(){
        $('.hexagon').not('.build').toggleClass('isHexTaken');
        $('.build').toggleClass('disabled');
    });

    $('.setBuilding').click(function(){
        var buildType = $(this).attr('name');
        $('.hexagon').not('.build').toggleClass('isHexTaken');
        $('.build').toggleClass('disabled');
        $('.hexagon.isHexTaken').on('click', function(event){
            var hexId = $(this).attr('id');
            window.location.replace("/build/"+hexId+"/"+buildType+"");
        });
    });
    $('.setResident').click(function(){
        $('.hexagon').not('.build').toggleClass('isHexTaken');
        $('.build').toggleClass('disabled');
//        $('.hexagon.isHexTaken').on('click', function(event){
//            var hexId = $(this).attr('id');
//            window.location.replace("/build/"+hexId+"/"+maxResident+"");
//        });
    });
//    $('.hexagon').click(function(){
//        var hexId = $(this).attr('id');
//        var result = $(this).closest('main').find('#result');
//        result.html('<p>'+hexId+'</p>');
//    });

    $('.hexagon').click(function(){
        var hexId = $(this).attr('id');
        var hexInfoBox = $(this).closest('main').find('#hexInfoBox');
        var result = $(this).closest('main').find('#result');
        result.html('<p>'+hexId+'</p>');
        hexInfoBox.children('.hexInfoBoxDetail').hide();
        hexInfoBox.children('.hexInfoBoxDetail#hexBox'+hexId+'').toggle('slow');
    });

    $('.buildingToHide').click(function(){
        $(this).next().toggle('slow');
    });

});

//    $('.hexagon').mouseover(function(){
//        var hex_id = $(this).attr('id');
//        $('.hexInfoBoxDetail#hexBox'+hex_id+'').show();
//    }).mouseout(function(){
//        var hex_id = $(this).attr('id');
//        $('.hexInfoBoxDetail#hexBox'+hex_id+'').hide();
//        });