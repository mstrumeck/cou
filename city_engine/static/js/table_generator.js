$(document).ready(function() {
    $('.hexagon#1').mouseover(function(){
        $('.hexInfoDetail').show();
    }).mouseout(function(){
        $('.hexInfoDetail').hide();
    });

    $('#hex-change').click(function(){
    $('.hexagon').toggleClass('change-hex');
    });

    $('.hexagon').click(function(){
        $(this).closest('div').children('.detail-hex-info').toggle('fast');
    });



});

