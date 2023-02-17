//<script type="text/javascript">
//
//$('.js-captcha-refresh').click(function(){
//    $form = $(this).parents('form');
//
//    $.getJSON($(this).data('url'), {}, function(json) {
//        // This should update your captcha image src and captcha hidden input
//    });
//
//    return false;
//});
//
//$('.captcha').click(function () {
//    $.getJSON("/captcha/refresh/", function (result) {
//        $('.captcha').attr('src', result['image_url']);
//        $('#id_captcha_0').val(result['key'])
//    });
//});
//
//</script>

/*
* Credits go to https://stackoverflow.com/a/20371801/8504344, https://stackoverflow.com/users/179024/mw
*/
$(document).ready(function () {
    // Add refresh button after field (this can be done in the template as well)
    $('img.captcha').after(
        $('<a href="#void" class="captcha-refresh"><i class="fa fa-refresh"></i></a>')
    );

    // Click-handler for the refresh-link
    $('.captcha-refresh').click(function () {
        var $form = $(this).parents('form');
        var url = location.protocol + "//" + window.location.hostname + ":"
            + location.port + "/captcha/refresh/";

        // Make the AJAX-call
        $.getJSON(url, {}, function (json) {
            $form.find('input[name="captcha_0"]').val(json.key);
            $form.find('img.captcha').attr('src', json.image_url);
        });

        return false;
    });
});