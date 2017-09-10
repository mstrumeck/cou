$(document).ready(function() {
    $('.detail-hex-info').hide();
    $('#hex-change').click(function(){
    $('.hexagon').toggleClass('change-hex');
    });

    $('.hexagon').click(function(){
        $(this).closest('div').children('.detail-hex-info').toggle('slow');
    });

});

