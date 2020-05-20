$(function () {
    $('#user-table').DataTable();
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

function renewHost(renewId, mac) {
    // Strip the id to get parent id
    let baseId = renewId.substring(6);
    // let element = document.getElementById(id);


    // Send an AJAX request to renew the record
    $.ajax({
        url: `/api/hosts/${mac}/renew/`,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken'),
            'sessionid': $.cookie('sessionid'),
        },
        data: {
            expire_days: 365,
        },
        success: res => {
            // Update displayed expiration
            let expire_days = Number(res.expire_days);
            let expire_display = document.getElementById(`expire-${baseId}`);

            if (expire_days <= 30)
                expire_display.classList.add('near-exp');
            else
                expire_display.classList.remove('near-exp');

            if (expire_days === 0)
                expire_display.innerText = 'Today';
            else if (expire_days < 0)
                expire_display.innerText = 'Expired';
            else if (!expire_days)
                expire_display.innerText = 'None';
            else
                expire_display.innerText = `${expire_days} ${expire_days > 1 ? 'days' : 'day'}`;
        }
    });
}