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
            { "bSortable": false },
            null,
            { "bSortable": false },
            { "bSortable": false },
            { "bSortable": false },
            { "bSortable": false },
        ],
        "fnInitComplete": function() {
            this.fnAdjustColumnSizing(true);

            $('#id_search').yourlabsAutocomplete({
                url: '/api/web/IPAMHostSearchAutoComplete',
                choiceSelector: '[data-value]',
                minimumCharacters: 2,
                placeholder: 'Advanced Search',
                getQuery: function() {
                    var value = this.input.val();
                    return value.substr(value.lastIndexOf(':') + 1);
                },
                refresh: function() {
                    var value = this.input.val();
                    this.current_search = value.substr(0, value.lastIndexOf(':'));
                    this.search_type = value.split(" ");
                    this.search_type = this.search_type[this.search_type.length - 1];
                    this.search_type = this.search_type.substr(0, this.search_type.lastIndexOf(':') + 1);

                    var searches = ['user:', 'group:', 'net:']
                    var do_search = false;

                    if (searches.indexOf(this.search_type) != -1) {
                        var do_search = true;
                        this.value = this.getQuery();
                    }
                    else {
                        this.hide();
                        do_search = false;
                    }

                    if (do_search) {
                        // If the input doesn't contain enought characters then abort, else fetch.
                        this.value.length < this.minimumCharacters ? this.hide() : this.fetch();
                    }
                },
            }).input.bind('selectChoice', function(event, choice, autocomplete) {
                var value = choice.attr('data-value');
                this.value = autocomplete.current_search + ':' + value;
            });

            $('#id_search').on('keyup change', function(){
                var value = $(this).val() ? $(this).val() : '';

                delay(function(){
                    $.cookie('search_filter', value, {expires: 1, path: '/hosts/'});
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

                $("#result_list span.flagged").parents('tr').addClass('flagged');

                $(".host-details").click(function(){
                    var hostname = $(this).prop("rel");
                    var href = $(this).prop("href");
                    var edit_href = $(this).prop("id");

                    $('#host-details').modal({
                          remote: href
                    });

                    $('#host-details').on('shown', function(){
                        $("#host-detail-label").text("Details for: " + hostname);
                        $("#edit-host").prop("href", edit_href);
                    });

                    return false;
                });

                $('#host-details').on('hidden', function() {
                    $(this).data('modal').$element.removeData();
                    $(".modal-body").html('Loading...');
                });

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
        },
        "fnInfoCallback": function(oSettings, iStart, iEnd, iMax, iTotal, sPre ) {
            if (iTotal < iMax){
                $("#filtered-label").show();
                return "Showing " + iStart + " to " + iEnd + " of " + iTotal + " entries (filtered from " + iMax + " total entries)"
            }
            else {
                $("#filtered-label").hide();
                return "Showing " + iStart + " to " + iEnd + " of " + iTotal + " entries"
            }
        }
    });

    var pageOnchange = function() {
        var s=(document.body.scrollTop||document.documentElement.scrollTop) + window.innerHeight;
        if(s<height){page_bar.addClass('fixed');}
        else{page_bar.removeClass('fixed');}
    }

    $('#changelist-form').bind("keyup keypress", function(e) {
      var code = e.keyCode || e.which;
      if (code  == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#changelist-filters-toggle").click(function() {
        $("#changelist-filter-actions").toggle();
        $(this).toggleClass('btn-inverse');
    });


    $("#search-info-close").click(function() {
        $("#search-help").hide();
    });

    //Triger filtering on owners
    $("#filter-owners button").click(function() {
        $("#filter-owners button").removeClass('btn-inverse');
        $(this).addClass('btn-inverse');
        $.cookie('owner_filter', $(this).val(), {expires: 1, path: '/hosts/'});
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
        $.removeCookie('search_filter', {path: '/hosts/'});
        $("#id_search").val('');
        results.fnFilterClear();
        return false;
    });

    $(".search_init").on('keyup change', function() {
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
        if ($(this).is(":checked")) {
            $(".action-select").prop('checked', 'checked');
        }
        else {
            $(".action-select").prop('checked', '');
        }
    });

    // Action submit logic
    $("#action-submit").click(function() {
        var action = $("#host-action").val();
        var hosts = $(".action-select:checked");

        if (hosts.length > 0) {
            if (action == 'owners') {
                $('#host-owners').modal();
            }
            else if (action == 'delete') {
                var res = confirm("Are you sure you want to delete the selected hosts?")
                if (res == true) {
                    return true;
                }
            }
            else if (action == 'renew') {
                $('#host-renew').modal();
            }
        }
        else {
            alert('Please select one or more hosts to perform this action.')
        }

        return false;
    });

});
