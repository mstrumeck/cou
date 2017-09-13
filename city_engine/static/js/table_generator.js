$(document).ready(function() {

    $('.hexagon').mouseover(function(){
        var hex_id = $(this).attr('id');
        $('.hexInfoDetail#hexBox'+hex_id+'').show();
    }).mouseout(function(){
        var hex_id = $(this).attr('id');
        $('.hexInfoDetail#hexBox'+hex_id+'').hide();
        });

    $('.hexagon').select(function(){
        var hex_id = $(this).attr('id');
        $(this).toggleClass('changeHex');
        $('.hexInfoDetail#hexBox'+hex_id+'').show();
    });

//    $('.hexagon').selectable({
//        filter: '.hexagon-middle'
//    });

    $('#hex-change').click(function(){
    $('.hexagon').toggleClass('changeHex');
    });

    $('.hexagon').click(function(){
        $(this).closest('div').children('.hexInfoDetail').toggle('fast');
    });



});

