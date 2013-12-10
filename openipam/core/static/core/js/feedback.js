$(function() {
    $('div#feedback div.handle').click( function() {
        var leftStr = "0px";
        ($("div#feedback").css("left") == "0px") ? leftStr="-280px" : leftStr="0px";
        $("div#feedback").animate({ left: leftStr }, 500 );
        console.log('hi')
    });

    $('#feedback-form input[type="submit"]').click( function() {

        if ($('#id_type').val() == '' || $('#id_comment').val() == ''){
            alert('Both the type and detail fields are required.');
            return false;
        }

        var sendingMsg = ' \
            <div class="feedback-sending alert alert-info"> \
                <button type="button" class="close" data-dismiss="alert">×</button> \
                Sending... \
            </div> \
        ';

        var successMsg = ' \
            <div class="alert alert-success"> \
                <button type="button" class="close" data-dismiss="alert">×</button> \
                Thank you for your feedback. \
            </div> \
        ';

        var errorMsg = ' \
            <div class="alert alert-error"> \
                <button type="button" class="close" data-dismiss="alert">×</button> \
                Something went wrong and your message could not be sent. \
            </div> \
        ';

        $('#feedback-form').prepend(sendingMsg);

        // $('#feedback-form').fadeOut(400, function() {
        //     $('div.feedback-sending').fadeIn();
        // });

        var csrftoken = $.cookie('csrftoken');

        // Submit the form via Ajax
        $.ajax({
            type: "post",
            url: '/request/',
            data: {
                "type" : $('#id_type').val(),
                "comment" : $('#id_comment').val()
            },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function() {
                $('div.feedback-sending').fadeOut(400, function() {
                    $('#feedback-form').prepend(successMsg).fadeIn();
                    $(this).remove();
                });
                return false;
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                $('#feedback-form').prepend(errorMsg);
                return false;
            }
        });

        return false;
    });

    $(".feedback-cancel").click(function(){
        $("#feature-toggle").click();
    });
});



