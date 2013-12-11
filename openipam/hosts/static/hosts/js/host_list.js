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
            { "bSortable": false },
            null,
            { "bSortable": false },
            { "bSortable": false },
            { "bSortable": false },
            { "bSortable": false },
        ],
        "fnInitComplete": function() {
            this.fnAdjustColumnSizing(true);
        },
        "fnServerParams": function (aoData) {
            aoData.push(
                { "name": "group_filter", "value": $.cookie('group_filter') }
            );
            aoData.push(
                { "name": "user_filter", "value": $.cookie('user_filter') }
            );
            aoData.push(
                { "name": "owner_filter", "value": $.cookie('owner_filter') }
            );
        },
        "fnServerData": function(sSource, aoData, fnCallback) {
            $.getJSON(sSource, aoData, function(json) {

                // Populate Table
                fnCallback(json);

                $("#result_list span.expired-date").parents('tr').addClass('expired');

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

            //return iStart +" to "+ iEnd;
        }
    });

    var pageOnchange = function() {
        var s=(document.body.scrollTop||document.documentElement.scrollTop) + window.innerHeight;
        if(s<height){page_bar.addClass('fixed');}
        else{page_bar.removeClass('fixed');}
    }

    $("#changelist-filters-toggle").click(function() {
        $("#changelist-filter-actions").toggle();
        $(this).toggleClass('btn-inverse');
    });


    $("#filter-close").click(function() {
        $("#changelist-filters-toggle").click();
    });


    // Trigger filtering on group
    $("#id_groups").unbind('change').change(function() {
        $.cookie('group_filter', $(this).val(), {expires: 1, path: '/hosts/'});
        results.fnDraw();
    });

    // Trigger filtering on group
    $("#id_users").unbind('change').change(function() {
        $.cookie('user_filter', $(this).val(), {expires: 1, path: '/hosts/'});
        results.fnDraw();
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
        $("#id_users-deck .remove").click();
        $("#id_groups-deck .remove").click();
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
