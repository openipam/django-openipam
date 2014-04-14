$(function() {
    if ($('#id_mimic_select').length > 0) {
        $('#id_mimic_select').yourlabsAutocomplete({
            url: '/api/web/UserAutocomplete/',
            choiceSelector: '[data-value]',
            minimumCharacters: 1,
            placeholder: 'Mimic User'
        }).input.bind('selectChoice', function(event, choice, autocomplete) {
            $("#id_mimic_value").val(choice.attr('data-value'));
            $("#mimic_form").submit();
        });
    }
});
