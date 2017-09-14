$(document).ready(function() {
    $('#hex-change').click(function(){
        $('.hexagon').toggleClass('changeHex');
    });

    $('.hexagon').click(function(){
        var hex_id = $(this).attr('id');
        $(this).closest('main').find('#hexInfoBox').children('.hexInfoBoxDetail').hide();
        $(this).closest('main').find('#hexInfoBox').children('.hexInfoBoxDetail#hexBox'+hex_id+'').toggle();

    });
});