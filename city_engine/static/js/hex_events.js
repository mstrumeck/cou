$(document).ready(function() {

    $('#hex-change').click(function(){
        $('.hexagon').not('.build').toggleClass('isHexTaken');
        $('.build').toggleClass('disabled');
    });

    $('#buildPowerPlant').click(function(){
        var buildType = $(this).attr('value');
        $('.hexagon').not('.build').toggleClass('isHexTaken');
        $('.build').toggleClass('disabled');
        $('.hexagon.isHexTaken').on('click', function(event){
            var hexId = $(this).attr('id');
            window.location.replace("/build/"+hexId+"/"+buildType+"");
        });

    });

    $('.hexagon').click(function(){
        var hexId = $(this).attr('id');
        var hexInfoBox = $(this).closest('main').find('#hexInfoBox');
        hexInfoBox.children('.hexInfoBoxDetail').hide();
        hexInfoBox.children('.hexInfoBoxDetail#hexBox'+hexId+'').toggle('slow');
    });
});

//    $('.hexagon').mouseover(function(){
//        var hex_id = $(this).attr('id');
//        $('.hexInfoBoxDetail#hexBox'+hex_id+'').show();
//    }).mouseout(function(){
//        var hex_id = $(this).attr('id');
//        $('.hexInfoBoxDetail#hexBox'+hex_id+'').hide();
//        });