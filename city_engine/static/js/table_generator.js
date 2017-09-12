$(document).ready(function() {

    $('.hexagon').mouseover(function(){
        var id_text = $(this).attr('id');
        $('.hexInfoDetail#hexBox'+id_text+'').show();
    }).mouseout(function(){
        var id_text = $(this).attr('id');
        $('.hexInfoDetail#hexBox'+id_text+'').hide();
        });

    $('#hex-change').click(function(){
    $('.hexagon').toggleClass('change-hex');
    });

    $('.hexagon').click(function(){
        $(this).closest('div').children('.detail-hex-info').toggle('fast');
    });



});

