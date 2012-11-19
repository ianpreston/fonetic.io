$(function() {
    $('a[data-role="delete-clip"]').click(function() {
        var $t = $(this);
        var clip_id = $t.data('clip-id');
        $.post('/admin/clips/delete/' + clip_id, function() {
            $t.closest('*[data-role="admin-clip-container"]').remove();
        });
    });
});