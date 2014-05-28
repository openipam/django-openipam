$(function(){

    var oCache = {
        iCacheLower: -1
    };

    function fnSetKey( aoData, sKey, mValue )
    {
        for ( var i=0, iLen=aoData.length ; i<iLen ; i++ )
        {
            if ( aoData[i].name == sKey )
            {
                aoData[i].value = mValue;
            }
        }
    }

    function fnGetKey( aoData, sKey )
    {
        for ( var i=0, iLen=aoData.length ; i<iLen ; i++ )
        {
            if ( aoData[i].name == sKey )
            {
                return aoData[i].value;
            }
        }
        return null;
    }


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
        "sDom": '<"header well well-sm"r>t<"paginator well well-sm"lpi<"clear">>',
        "aaSorting": [[ 1, "asc" ]],
        "oLanguage": {
            "sLengthMenu": "Show _MENU_ records",
            "sSearch": ""
        },
        "stateLoaded": function (settings, data) {
            $("#s_host").val(data.aoSearchCols[0].sSearch);
            $("#s_mac").val(data.aoSearchCols[1].sSearch);
            $("#s_ip").val(data.aoSearchCols[2].sSearch);
            $("#s_expires").val(data.aoSearchCols[3].sSearch);
        },
        "aoColumns": [
            { "bSortable": false },
            null,
            null,
            null,
            null,
            { "bSortable": false },
            { "bSortable": false },
            { "bSortable": false },
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
                    return value;
                },
                refresh: function() {
                    var value = this.input.val();
                    var current_search = value.substr(value.lastIndexOf(':') + 1);
                    this.search_type = value.split(" ");
                    this.search_type = this.search_type[this.search_type.length - 1];
                    this.search_type = this.search_type.substr(0, this.search_type.lastIndexOf(':') + 1);

                    var searches = ['user:', 'group:', 'net:']
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
            var iPipe = 10; /* Ajust the pipe size */

            var bNeedServer = false;
            var sEcho = fnGetKey(aoData, "sEcho");
            var iRequestStart = fnGetKey(aoData, "iDisplayStart");
            var iRequestLength = fnGetKey(aoData, "iDisplayLength");
            var iRequestEnd = iRequestStart + iRequestLength;
            oCache.iDisplayStart = iRequestStart;

            /* outside pipeline? */
            if ( oCache.iCacheLower < 0 || iRequestStart < oCache.iCacheLower || iRequestEnd > oCache.iCacheUpper )
            {
                bNeedServer = true;
            }

            /* sorting etc changed? */
            if ( oCache.lastRequest && !bNeedServer )
            {
                for( var i=0, iLen=aoData.length ; i<iLen ; i++ )
                {
                    if ( aoData[i].name != "iDisplayStart" && aoData[i].name != "iDisplayLength" && aoData[i].name != "sEcho" )
                    {
                        if ( aoData[i].value != oCache.lastRequest[i].value )
                        {
                            bNeedServer = true;
                            break;
                        }
                    }
                }
            }

            /* Store the request for checking next time around */
            oCache.lastRequest = aoData.slice();

            if ( bNeedServer )
            {
                if ( iRequestStart < oCache.iCacheLower )
                {
                    iRequestStart = iRequestStart - (iRequestLength*(iPipe-1));
                    if ( iRequestStart < 0 )
                    {
                        iRequestStart = 0;
                    }
                }

                oCache.iCacheLower = iRequestStart;
                oCache.iCacheUpper = iRequestStart + (iRequestLength * iPipe);
                oCache.iDisplayLength = fnGetKey( aoData, "iDisplayLength" );
                fnSetKey( aoData, "iDisplayStart", iRequestStart );
                fnSetKey( aoData, "iDisplayLength", iRequestLength*iPipe );

                $.getJSON( sSource, aoData, function (json) {
                    /* Callback processing */
                    oCache.lastJson = jQuery.extend(true, {}, json);

                    if ( oCache.iCacheLower != oCache.iDisplayStart )
                    {
                        json.aaData.splice( 0, oCache.iDisplayStart-oCache.iCacheLower );
                    }
                    json.aaData.splice( oCache.iDisplayLength, json.aaData.length );

                    fnCallback(json)
                });
            }
            else
            {
                json = jQuery.extend(true, {}, oCache.lastJson);
                json.sEcho = sEcho; /* Update the echo for each response */
                json.aaData.splice( 0, iRequestStart-oCache.iCacheLower );
                json.aaData.splice( iRequestLength, json.aaData.length );
                fnCallback(json);
            }

            $("#result_list span.flagged").parents('tr').addClass('flagged');

            // $(".host-details").click(function(){
            //     var hostname = $(this).prop("rel");
            //     var href = $(this).prop("href");
            //     var edit_href = $(this).prop("id");

            //     $('#host-details').modal({
            //           remote: href
            //     });

            //     $('#host-details').on('shown', function(){
            //         $("#host-detail-label").text("Details for: " + hostname);
            //         $("#edit-host").prop("href", edit_href);
            //     });

            //     return false;
            // });

            $(".host-details").on('click', function() {
                var a = $(this);
                var tr = $(this).parents('tr')[0];
                var hostname = $(this).prop("rel");
                var href = $(this).prop("href");
                var edit_href = $(this).prop("id");
                var detail_html = $(tr).next("tr").has("td.host-detail");

                if (detail_html.length > 0) {
                    detail_html.toggle();
                    $(this).find('span').toggleClass('glyphicon-chevron-down').toggleClass('glyphicon-chevron-right');
                }
                else {
                    $.ajax({
                        url: href,
                        beforeSend: function() {
                            $("#result_list_processing").css('visibility', 'visible').show();
                        },
                        complete: function() {
                            $("#result_list_processing").css('visibility', 'hidden').hide();
                        },
                        success: function(data) {
                            $(a).find('span').removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down');
                            results.fnOpen(tr, data, 'host-detail');
                        }
                    });
                }

                return false;
            } );

            $('#host-details').on('hidden', function() {
                $(this).data('modal').$element.removeData();
                $(".modal-body").html('Loading...');
            });

            // Set pagination to stick when scrolling
            var page_bar = $('.paginator');
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

            return;

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
        $("#filter-owners button").removeClass('active');
        $(this).addClass('active');
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

    $(".search_init").on('input', function() {
        /* Filter on the column (the index) of this element */
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
