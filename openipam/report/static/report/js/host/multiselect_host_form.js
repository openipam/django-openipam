const chunk = (arr, chunkSize) => {
  const chunks = [];
  let chunk = 0;
  for (let i = 0; i < arr.length; ++i, chunk = Math.floor(i / chunkSize)) {
    const curr = arr[i];
    if (chunk > chunks.length - 1) {
      chunks.push([curr]);
      continue;
    }
    chunks[chunk].push(curr);
  }
  return chunks;
};

const toggleAllCheckboxes = (check = true) =>
  $("input[type=checkbox]").each(function () {
    $(this).prop("checked", check);
  });

const macCount = (form) =>
  $(form)
    .serializeArray()
    .filter((input) => input.name === "mac_addr[]").length;

const submitForm = (form) => {
  // workaround for nginx 400 when mac_addr array is too long; split it into chunks and request
  const chunkSize = 200;
  const submitPromises = chunk($(form).serializeArray("mac_addr"), chunkSize)
    .map((chunkFormData) =>
      chunkFormData
        .filter(({ name }) => name == "mac_addr[]")
        .map(({ value }) => value)
    )
    .map((chunk) => {
      const thisChunkData = new FormData($(form).get(0));
      thisChunkData.delete("mac_addr[]");

      chunk.forEach((macAddr) => thisChunkData.append("mac_addr[]", macAddr));

      return new Promise((res, rej) => {
        $.ajax({
          url: $(form).attr("action"),
          type: "POST",
          data: new URLSearchParams(thisChunkData).toString(),
          success: (data) => res(data),
          error: (data) => rej(data),
        });
      });
    });
  return Promise.all(submitPromises);
};

const toggle = {
  "btn-primary": "btn-warning",
  "btn-warning": "btn-primary",
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
