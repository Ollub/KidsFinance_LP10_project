
(function($) {
    $('#register-new-user').on('click', function(e) {
        e.preventDefault();
        pass = $('#password-input-register').val();
        reentered_pass = $('#password-confirmation').val();

        if (pass !== reentered_pass) {
            $reentered = $('.reentered');
            $reentered.text('Введённые вами пароли не совпадают');
            $reentered.css('color','#ff0000');
        } else {
            $('#new-user-form').submit();
        }
    });
})(jQuery);
