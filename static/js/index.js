$(function() {
    $('.terms-searchbox').keyup(function() {
        $('.terms-container').load('/terms/search?q=' + encodeURIComponent($('.terms-searchbox').val()));
    });
});