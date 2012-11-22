$(function() {
    $('.terms-searchbox').keyup(function() {
        var query = $('.terms-searchbox').val();
        $('.terms-container').load('/terms/search?q=' + encodeURIComponent(query));

        if (query.length > 0 && $('.intro-text').is(':hidden') == false) {
            $('.terms-container').show();
            $('.intro-text').fadeOut();
        }
        if (query.length == 0 && $('.intro-text').is(':hidden')) {
            $('.terms-container').hide();
            $('.intro-text').fadeIn();
        }
    });

    $('.intro-text').fadeIn(1500, function() {
        $('.terms-searchbox').focus();
    });
});