$(document).ready(function() {

//    $('.hexagon#1').mouseover(function(){
//        $('.hexInfoDetail#hexBox1').show();
//    }).mouseout(function(){
//        $('.hexInfoDetail#hexBox1').hide();
//        });
//
//    $('.hexagon#2').mouseover(function(){
//        $('.hexInfoDetail#hexBox2').show();
//    }).mouseout(function(){
//        $('.hexInfoDetail#hexBox2').hide();
//        });
//
//    $('.hexagon#3').mouseover(function(){
//        $('.hexInfoDetail#hexBox3').show();
//    }).mouseout(function(){
//        $('.hexInfoDetail#hexBox3').hide();
//        });
//    $('hexagon#1').hover(function(){
//        $('.hexInfoDetail#hexBox1').show();
//    }, function(){
//        $('.hexInfoDetail#hexBox1').hide();
//    });
    var text = $('.hexagon#1').attr('id');
    $('#test').text(text);

    $('.hexagon').mouseover(function(){
        var id_text = $(this).attr('id');
        $('.hexInfoDetail#hexBox'+id_text+'').show();
    }).mouseout(function(){
        $('.hexInfoDetail#hexBox'+id_text+'').hide();
        });

    $('#hex-change').click(function(){
    $('.hexagon').toggleClass('change-hex');
    });

    $('.hexagon').click(function(){
        $(this).closest('div').children('.detail-hex-info').toggle('fast');
    });



});

