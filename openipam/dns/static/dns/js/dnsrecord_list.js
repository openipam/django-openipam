$(function(){

    $.fn.dataTableExt.oApi.fnFilterClear = function(oSettings)
    {
        /* Remove global filter */
        oSettings.oPreviousSearch.sSearch = "";

        /* Remove the text of the global filter in the input boxes */
        if (typeof oSettings.aanFeatures.f != 'undefined')
        {
            var n = oSettings.aanFeatures.f;
            for (var i=0, iLen=n.length ; i<iLen ; i++)
            {
                $('input[type="text"]', n[i]).val( '' );
            }
        }

        /* Remove the search text for the column filters - NOTE - if you have input boxes for these
         * filters, these will need to be reset
         */
        for (var i=0, iLen=oSettings.aoPreSearchCols.length ; i<iLen ; i++)
        {
            oSettings.aoPreSearchCols[i].sSearch = "";
        }

        /* Redraw */
        oSettings.oApi._fnReDraw(oSettings);
    };

    var asInitVals = new Array();

    var results = $("#result_list").dataTable({
        "bPaginate": true,
        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": "data/",
        "sPaginationType": "full_numbers",
        "bAutoWidth": false,
        "bStateSave": true,
        "bJQueryUI": true,
        "sDom": '<"header well well-small"rf>t<"pagination well well-small"lpi><"clear">',
        "aaSorting": [[ 1, "asc" ]],
        "oLanguage": {
            "sLengthMenu": "Show _MENU_ records",
            "sSearch": ""
        },
        "aoColumns": [
            { "bSortable": false },
            null,
            null,
            null,
            null,
            null,
            { "bSortable": false },
        ],
        "fnInitComplete": function() {
            this.fnAdjustColumnSizing(true);
        },
        "fnServerParams": function (aoData) {
            aoData.push(
                { "name": "host_filter", "value": $.cookie('host_filter') }
            );
            aoData.push(
                { "name": "group_filter", "value": $.cookie('group_filter') }
            );
            aoData.push(
                { "name": "user_filter", "value": $.cookie('user_filter') }
            );
        },
        "fnServerData": function(sSource, aoData, fnCallback) {
            $.getJSON(sSource, aoData, function(json) {

                // Populate Table
                fnCallback(json);

                // Reset Edit all.
                $("a.edit-all").prop('rel', 'edit').html('Edit All');
                $("#action-toggle").removeAttr('checked');

                if ($.selectedRecords && $.formData) {
                    $.each($.selectedRecords, function(index, value) {
                        $("a.edit-dns[rel='"+ value +"']").click();
                        $("a.edit-dns[rel='"+ value +"']").parents('tr').removeClass('info').addClass('error');
                        $("input[name='name-"+ value +"'").val($.formData['name-'+ value]);
                        $("input[name='content-"+ value +"'").val($.formData['content-'+ value]);
                        $("input[name='type-"+ value +"'").val($.formData['type-'+ value]);
                    });
                }

                // Clone html for add row and attach it to datatable
                $("#add-table tr.add-row").appendTo("#result_list");

                // Set pagination to stick when scrolling
                var page_bar = $('.pagination');
                page_bar.removeClass('fixed');
                if(page_bar.length){
                    var height=page_bar[0].offsetTop + page_bar.outerHeight();
                    var onchange = function(){
                        var s=(document.body.scrollTop||document.documentElement.scrollTop) + window.innerHeight;
                        if(s<height){page_bar.addClass('fixed');}
                        else{page_bar.removeClass('fixed');}
                    }
                    window.onscroll=onchange;
                    onchange();
                }
            });
        }
    });

    var pageOnchange = function() {
        var s=(document.body.scrollTop||document.documentElement.scrollTop) + window.innerHeight;
        if(s<height){page_bar.addClass('fixed');}
        else{page_bar.removeClass('fixed');}
    }

    // Edit DNS record for a row
    $("#result_list").on('click', 'a.edit-dns', function() {
        var row = $(this).parents('tr');
        row.addClass('info').find("input[type='text'], select").show();
        row.find('input.action-select').prop('checked', 'checked');
        row.find("span").hide();
        $(this).hide();
        row.find('a.cancel-dns').show();
        $("#form-actions").show();
    });


    // Cancel DNS reocrd edit for a row
    $("#result_list").on('click', 'a.cancel-dns', function() {
        var row = $(this).parents('tr');
        row.removeClass('info error').find("input[type='text'], select").hide();
        row.find('input.action-select').removeAttr('checked');
        row.find("span").show();
        $(this).hide();
        row.find('a.edit-dns').show();

        var anyEditable = $("a.cancel-dns:visible")
        if (anyEditable.length == 0) {
            $("#form-actions").hide();
        }
    });

    // Cancel selection and form fields
    $("#result_list").on('click', '.action-select', function(){
        $(this).parents('tr').toggleClass('info');
        if (!$(this).is(':checked')) {
            $(this).parents('tr').find('a.cancel-dns').click();
        }
    });

    // Add another row to table when add record is clicked
    $("#result_list").on('click', "a.add-record", function() {
        var thisRow = $(this).parents('tr');
        var newRow = thisRow.clone();
        thisRow.find("a.add-record").remove();
        thisRow.find("a.remove-record").show();
        newRow.appendTo("#result_list");
    });

    // Remove row from table
    $("#result_list").on('click', "a.remove-record", function() {
        $(this).parents('tr').remove();
    });

    $("#result_list").on('change', ".add-row input, .add-row select", function() {
        $("#form-actions").show();
    });

    // Call edit all for all records
    $("a.edit-all").click(function() {
        if ($(this).prop('rel') == 'edit') {
            $(this).prop('rel', 'cancel');
            $(this).html('Cancel');
            $("a.edit-dns").click();
        }
        else {
            $(this).prop('rel', 'edit');
            $(this).html('Edit All');
            $("a.cancel-dns").click();
            $("#action-toggle").removeAttr('checked');
        }
    });

    // Cancel edit of all records
    $("#cancel-edit").click(function() {
        $("a.cancel-dns").click();
        $("#form-actions").hide();
        $("#action-toggle").removeAttr('checked');
        $(".add-row input, .add-row select").val('');
    });


    $("#changelist-filters-toggle").click(function() {
        $("#changelist-filter-actions").toggle();
        $(this).toggleClass('btn-inverse');
    });


    $("#filter-close").click(function() {
        $("#changelist-filters-toggle").click();
    });

    // Trigger filtering on group
    $("#id_groups").unbind('change').change(function() {
        var value = $(this).val() ? $(this).val() : '';
        $.cookie('group_filter', value, {expires: 1, path: '/dns/'});
        results.fnDraw();
    });

    // Trigger filtering on group
    $("#id_users").unbind('change').change(function() {
        var value = $(this).val() ? $(this).val() : '';
        $.cookie('user_filter', value, {expires: 1, path: '/dns/'});
        results.fnDraw();
    });

    // Trigger filtering on group
    $("#id_host").unbind('change').change(function() {
        var value = $(this).val() ? $(this).val() : '';
        $.cookie('host_filter', value, {expires: 1, path: '/dns/'});
        results.fnDraw();
    });

    // JS Styling :/
    $("div.header").append($("#actions"));
    $("#actions").append($("#result_list_processing")).append('<div class="clear"><!-- --></div>');
    $("#search-help-button").after($("#result_list_filter"));
    $("#result_list_filter input").prop('placeholder', 'Quick Search');
    //$("#changelist-search").prepend($("#result_list_length"));


    $("tfoot input").each(function (i){
        asInitVals[i] = this.value;
    });

    //$(".pagination").append("<div style='clear: both;'><!-- --></div>").append($("#form-actions").show());
    $(".pagination").prepend($("#form-actions"));
    $(".pagination").append("<div style='clear: both;'><!-- --></div>");

    // Clear all filters logic
    $("#clear-filters").click(function() {
        $(".dataTables_filter input[type='text']").val('');
        $(".search_init").val('');
        $("select.filter-select option").each(function(index, obj){
            if (index == 0){
                $(obj).attr('selected', 'selected');
            }
            else {
                $(obj).removeAttr('selected');
            }
        });
        $("#id_host-deck .remove").click();
        $("#id_users-deck .remove").click();
        $("#id_groups-deck .remove").click();

        $.removeCookie('host_filter', {path: '/dns/'});
        $.removeCookie('user_filter', {path: '/dns/'});
        $.removeCookie('group_filter', {path: '/dns/'});

        results.fnFilterClear();
        return false;
    });

    $(".search_init").bind('keyup change', function() {
        /* Filter on the column (the index) of this element */
        results.fnFilter($(this).val(), $(".search_init").index($(this)));
    });

    $("#search-help-button").click(function(){
        $("#search-help").toggle();
        return false;
    });

    // Toggle all select for checkboxes
    $("#action-toggle").click(function() {
        $.each($(".action-select"), function(key, selector){
            if ($("#action-toggle").is(':checked') && !$(selector).is(':checked')) {
                selector.click();
            }
            else if (!$("#action-toggle").is(':checked') && $(selector).is(':checked')) {
                selector.click();
            }
        });
    });

    // Action submit logic
    $("#action-submit").click(function() {
        var action = $("#host-action").val();
        var records = $(".action-select:checked");

        if (records.length > 0) {
            if (action == 'delete') {
                var res = confirm("Are you sure you want to delete the selected hosts?")
                if (res == true) {
                    return true;
                }
            }
        }
        else {
            alert('Please select one or more hosts to perform this action.')
        }

        return false;
    });

});
