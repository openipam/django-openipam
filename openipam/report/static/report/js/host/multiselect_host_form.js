const toggleAllCheckboxes = (check = true) =>
  $("input[type=checkbox]").each(function () {
    $(this).prop("checked", check);
  });

const macCount = (form) => $(form)
  .serializeArray()
  .filter((input) => input.name === "mac_addr[]")
  .length;

const submitForm = (form) =>
  new Promise((res, rej) => {
    $.ajax({
      url: $(form).attr("action"),
      type: "POST",
      data: $(form).serialize(),
      success: (data) => res(data),
      error: (data) => rej(data),
    })
  });

const toggle = {
  "btn-primary": "btn-warning",
  "btn-warning": "btn-primary"
};

$("#toggle-checks").on("click", function () {
  let newClass;
  Object.keys(toggle).forEach((key) => {
    if ($(this).hasClass(key)) {
      newClass = toggle[key];
    }
  });

  $(this).removeClass(toggle[newClass]);
  $(this).addClass(newClass);

  toggleAllCheckboxes(newClass === "btn-warning");
});