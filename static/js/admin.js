$(function() {
    $('a[data-role="delete-term"]').click(function() {
        var $t = $(this);
        var term_id = $t.data('term-id');
        $.post('/admin/terms/' + term_id + '/delete', function() {
            $t.closest('*[data-role="admin-term-container"]').remove();
        });
    });

    $('a[data-role="delete-clip"]').click(function() {
        var $t = $(this);
        var clip_id = $t.data('clip-id');
        $.post('/admin/clips/' + clip_id + '/delete', function() {
            $t.closest('*[data-role="admin-clip-container"]').remove();
        });
    });
});