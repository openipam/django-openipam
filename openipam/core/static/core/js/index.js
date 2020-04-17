$(function () {
    //     $('a[name=delete-host]').click(() => {
    //         console.log($(this));
    //         console.log($(this).prop('id'), 'clicked');
    //         $(this).hide();
    //     });

});

function deleteHost(delId, mac) {
    // Strip the id to get parent id
    let id = delId.substring(7);
    let element = document.getElementById(id);

    // Hide the element
    if (element.style.display === "none")
        element.style.display = "block";
    else
        element.style.display = "none";

    // Send an AJAX request to delete the record
    $.ajax({
        url: `/api/hosts/${mac}/delete/`,
        type: 'DELETE',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken'),
            'sessionid': $.cookie('sessionid')
        },
        success: res => {
            console.log(`${id} was deleted`);
        }
    });
}
