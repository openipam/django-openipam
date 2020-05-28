$(function () {
  if ($(this).width() <= 600)
    $('#th-actions').text('Edit');

  $('#user-table').DataTable();

  $(window).resize(function () {
    if ($(this).width() <= 600) {
      $('#th-actions').text('Edit');
    }
    else if ($(this).width() > 600) {
      $('#th-actions').text('Actions');
    }
  });

  refreshData();

  setInterval(refreshData, 10000)
});

function refreshData() {
  // Send an AJAX request to renew the record
  $.ajax({
    url: `/api/base/overview/`,
    type: 'GET',
    headers: {
      'X-CSRFToken': $.cookie('csrftoken'),
      'sessionid': $.cookie('sessionid'),
    },
    success: res => {
      $('#abandoned_leases').text(res.abandoned_leases);
      $('#active_leases').text(res.active_leases);
      $('#active_users').text(res.active_users);
      $('#dns_a_records').text(res.dns_a_records);
      $('#dns_cname_records').text(res.dns_cname_records);
      $('#dns_mx_records').text(res.dns_mx_records);
      $('#dynamic_hosts').text(res.dynamic_hosts);
      $('#static_hosts').text(res.static_hosts);
      $('#total_networks').text(res.total_networks);
      $('#user_dns_a').text(res.user_dns_a);
      $('#user_dns_a_sm').text(res.user_dns_a);
      $('#user_dns_cname').text(res.user_dns_cname);
      $('#user_dns_cname_sm').text(res.user_dns_cname);
      $('#user_dns_mx').text(res.user_dns_mx);
      $('#user_dns_mx_sm').text(res.user_dns_mx);
      $('#user_hosts_dynamic').text(res.user_hosts_dynamic);
      $('#user_hosts_dynamic_sm').text(res.user_hosts_dynamic);
      $('#user_hosts_static').text(res.user_hosts_static);
      $('#user_hosts_static_sm').text(res.user_hosts_static);
      $('#wireless_addresses_available').text(res.wireless_addresses_available);
      $('#wireless_addresses_total').text(res.wireless_addresses_total);
      $('#wireless_networks').text(res.wireless_networks);
    }
  });
}

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
      refreshData();
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