/**
 * Asynchronous function to return an { error? } when modal is confirmed
 * @callback onSubmitCallback
 * @return Promise<Object | null>
 */

/**
 * Function called when onSubmit contains no error
 * @callback onSuccessCallback
 */

/**
 * @param {string} confirmationTitle 
 * @param {string} confirmationMessage
 * @param {onSubmitCallback} onSubmit 
 * @param {onSuccessCallback} onSuccess
 */
$.fn.confirmHostsModal = function (confirmationTitle, confirmationMessage, onSubmit, onSuccess) {
  const render = (error) => {
    this.html(`
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <button
                type="button"
                class="close"
                data-dismiss="modal"
                aria-hidden="true"
              >
                &times;
              </button>
              <h3 class="modal-title">
                <span class="oaction"></span>
                ${confirmationTitle}
              </h3>
            </div>
            <div class="modal-body">
              <div class="clear">
                <p>
                  ${confirmationMessage}
                </p>
                ${error ? `
                  <div class="alert alert-danger" role="alert" id="error">
                    <span
                      class="glyphicon glyphicon-exclamation-sign"
                      aria-hidden="true"
                    ></span>
                    <span class="sr-only"></span>
                    Error: ${error}
                  </div>
                ` : ''}
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-danger ${error ? 'disabled' : ''}" id="confirm-modal-submit">Yes</button>
              <button
                class="btn btn-default"
                data-dismiss="modal"
                aria-hidden="true"
                id="cancel-delete"
              >
                No
              </button>
            </div>
          </div>
        </div>
      `);
    this.modal();
  }

  $("#error").hide();
  $("#confirm-modal-submit").removeClass("disabled");
  render();

  $("#confirm-modal-submit").on("click", async function () {
    $("#error").hide();
    $(this).addClass("disabled");

    const result = await onSubmit().catch((err) => err.responseJSON);

    if (!result) {
      render("Submission failed.");
    } else if (result.error) {
      render(result.error);
    } else {
      onSuccess();
    }
  });
}