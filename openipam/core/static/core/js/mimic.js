$(function() {
    if ($('#id_mimic_select').length > 0) {
        $('#id_mimic_select').select2({
            ajax: {
                url: "/api/autocomplete/mimicuser",
                dataType: "json"
            },
            minimumInputLength: 1,
            placeholder: 'Mimic User',
            width: "element",
        }).on('select2:selecting', function(e) {
            $("#id_mimic_value").val(e.params.args.data.choiceValue);
            $("#mimic_form").submit();
        });
    }
});
