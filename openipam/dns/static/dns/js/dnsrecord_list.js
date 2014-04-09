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

    var delay = (function(){
        var timer = 0;
        return function(callback, ms){
          clearTimeout (timer);
          timer = setTimeout(callback, ms);
        };
    })();

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
        "sDom": '<"header well well-small"r>t<"pagination well well-small"lpi><"clear">',
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

            $('#id_search').yourlabsAutocomplete({
                url: '/api/web/IPAMSearchAutoComplete',
                choiceSelector: '[data-value]',
                minimumCharacters: 2,
                placeholder: 'Advanced Search',
                getQuery: function() {
                    var value = this.input.val();
                    return value
                },
                refresh: function() {
                    var value = this.input.val();
                    var current_search = value.substr(value.lastIndexOf(':') + 1);
                    this.search_type = value.split(" ");
                    this.search_type = this.search_type[this.search_type.length - 1];
                    this.search_type = this.search_type.substr(0, this.search_type.lastIndexOf(':') + 1);

                    var searches = ['user:', 'group:']
                    var do_search = false;

                    if (searches.indexOf(this.search_type) != -1 && current_search != "") {
                        var do_search = true;
                        this.value = this.getQuery();
                    }
                    else {
                        this.hide();
                        do_search = false;
                    }

                    if (do_search) {
                        // If the input doesn't contain enought characters then abort, else fetch.
                        current_search < this.minimumCharacters ? this.hide() : this.fetch();
                    }
                },
            }).input.bind('selectChoice', function(event, choice, autocomplete) {
                var value = choice.attr('data-value');
                this.value = value;
            });

            $('#id_search').on('input selectChoice', function(){
                var value = $(this).val() ? $(this).val() : '';

                delay(function(){
                    $.cookie('search_filter', value, {expires: 1, path: '/dns/'});
                    results.fnDraw();
                }, 300);
            });


        },
        "fnServerParams": function (aoData) {
            aoData.push(
                { "name": "owner_filter", "value": $.cookie('owner_filter') }
            );
            aoData.push(
                { "name": "search_filter", "value": $.cookie('search_filter') }
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
                        $("input[name='ttl-"+ value +"'").val($.formData['ttl-'+ value]);
                        $("input[name='content-"+ value +"'").val($.formData['content-'+ value]);
                        $("input[name='type-"+ value +"'").val($.formData['type-'+ value]);
                    });
                }

                // Clone html for add row and attach it to datatable
                $("#add-table tr.add-row:not(.extra)").appendTo("#result_list");
                $("#add-table tr.add-row.extra").clone().appendTo("#result_list");

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

                formActionCheck();
            });
        },
        "fnInfoCallback": function(oSettings, iStart, iEnd, iMax, iTotal, sPre ) {
            if (iTotal < iMax){
                $("#filtered-label").show();
                $(".search_init, #id_search").each(function(){
                    if ($(this).val() != '') {
                        $(this).addClass('red-highlight');
                    }
                });
                return "Showing " + iStart + " to " + iEnd + " of " + iTotal + " entries (filtered from " + iMax + " total entries)"
            }
            else {
                $("#filtered-label").hide();
                $(".search_init, #id_search").removeClass('red-highlight');
                return "Showing " + iStart + " to " + iEnd + " of " + iTotal + " entries"
            }
        }
    });

    var pageOnchange = function() {
        var s=(document.body.scrollTop||document.documentElement.scrollTop) + window.innerHeight;
        if(s<height){page_bar.addClass('fixed');}
        else{page_bar.removeClass('fixed');}
    }

    var formActionCheck = function() {
        var selectedRecords = $.selectedRecords ? $.selectedRecords : []
        var anyEditable = $("a.cancel-dns:visible")

        if (selectedRecords.length > 0 || $("tr.add-row:not(.extra)").length > 0 || anyEditable.length > 0) {
            $("#form-actions").show();
        }
        else {
            $("#form-actions").hide();
        }
    }

    $('#changelist-form').bind("input", function(e) {
      var code = e.keyCode || e.which;
      if (code  == 13) {
        e.preventDefault();
        return false;
      }
    });

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
        var actionSelect = row.find('input.action-select');
        row.removeClass('info error').find("input[type='text'], select").hide();
        actionSelect.removeAttr('checked');
        row.find("span").show();
        $(this).hide();
        row.find('a.edit-dns').show();

        if ($.selectedRecords) {
            $.selectedRecords = $.selectedRecords.splice(actionSelect.val(), 1)
        }
        formActionCheck();
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

        formActionCheck();
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

    //Triger filtering on owners
    $("#filter-owners button").click(function() {
        $("#filter-owners button").removeClass('btn-inverse');
        $(this).addClass('btn-inverse');
        $.cookie('owner_filter', $(this).val(), {expires: 1, path: '/dns/'});
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

        $.removeCookie('search_filter', {path: '/dns/'});
        $("#id_search").val('');

        results.fnFilterClear();
        return false;
    });

    $(".search_init").bind('input', function() {
        var self = this;
        delay(function(){
            results.fnFilter($(self).val(), $(".search_init").index($(self)));
        }, 300);
    });

    $(".filter_init").on('change', function() {
        /* Filter on the column (the index) of this element */
        var self = this;
        delay(function(){
            results.fnFilter($(self).val(), $(".search_init").index($(self)));
        }, 300);

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
