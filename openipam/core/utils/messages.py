from django.contrib import messages


def process_errors(request, error_list=None, form=None, base_msg=None):
    if base_msg:
        messages.add_message(request, messages.ERROR, base_msg)

    if form:
        for key, errors in list(form.errors.items()):
            for error in errors:
                messages.add_message(request, messages.ERROR, error)

    for error in error_list:
        messages.add_message(request, messages.ERROR, error)
