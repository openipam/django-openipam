$(function(){
    $.getUrlVars = function() {
        var vars = {};
        var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
            vars[key] = value;
        });
        return vars;
    }
    $.urlVars = $.getUrlVars();

    //
    // Pipelining function for DataTables. To be used to the `ajax` option of DataTables
    //
    $.fn.dataTable.pipeline = function(opts) {
        // Configuration options
        var conf = $.extend({
            pages: 5,     // number of pages to cache
            url: '',      // script url
            data: null,   // function or object with parameters to send to the server
                          // matching how `ajax.data` works in DataTables
            method: 'GET' // Ajax HTTP method
        }, opts);

        // Private variables for storing the cache
        var cacheLower = -1;
        var cacheUpper = null;
        var cacheLastRequest = null;
        var cacheLastJson = null;

        return function (request, drawCallback, settings) {
            var ajax          = false;
            var requestStart  = request.start;
            var requestLength = request.length;
            var requestEnd    = requestStart + requestLength;

            if (settings.clearCache) {
                // API requested that the cache be cleared
                ajax = true;
                settings.clearCache = false;
            }
            else if (cacheLower < 0 || requestStart < cacheLower || requestEnd > cacheUpper) {
                // outside cached data - need to make a request
                ajax = true;
            }
            else if ( JSON.stringify( request.order )   !== JSON.stringify( cacheLastRequest.order ) ||
                      JSON.stringify( request.columns ) !== JSON.stringify( cacheLastRequest.columns ) ||
                      JSON.stringify( request.search )  !== JSON.stringify( cacheLastRequest.search )
            ) {
                // properties changed (ordering, columns, searching)
                ajax = true;
            }

            // Store the request for checking next time around
            cacheLastRequest = $.extend( true, {}, request );

            if ( ajax ) {
                // Need data from the server
                if ( requestStart < cacheLower ) {
                    requestStart = requestStart - (requestLength*(conf.pages-1));

                    if ( requestStart < 0 ) {
                        requestStart = 0;
                    }
                }

                cacheLower = requestStart;
                cacheUpper = requestStart + (requestLength * conf.pages);

                request.start = requestStart;
                request.length = requestLength*conf.pages;

                // Provide the same `data` options as DataTables.
                if ( $.isFunction ( conf.data ) ) {
                    // As a function it is executed with the data object as an arg
                    // for manipulation. If an object is returned, it is used as the
                    // data object to submit
                    var d = conf.data( request );
                    if ( d ) {
                        $.extend( request, d );
                    }
                }
                else if ( $.isPlainObject( conf.data ) ) {
                    // As an object, the data given extends the default
                    $.extend( request, conf.data );
                }

                settings.jqXHR = $.ajax( {
                    "type":     conf.method,
                    "url":      conf.url,
                    "data":     request,
                    "dataType": "json",
                    "cache":    false,
                    "success":  function ( json ) {
                        cacheLastJson = $.extend(true, {}, json);

                        if ( cacheLower != requestStart ) {
                            json.data.splice( 0, requestStart-cacheLower );
                        }
                        json.data.splice( requestLength, json.data.length );

                        drawCallback( json );
                    }
                } );
            }
            else {
                json = $.extend( true, {}, cacheLastJson );
                json.draw = request.draw; // Update the echo for each response
                json.data.splice( 0, requestStart-cacheLower );
                json.data.splice( requestLength, json.data.length );

                drawCallback(json);
            }
        }
    }

    // Register an API method that will empty the pipelined data, forcing an Ajax
    // fetch on the next draw (i.e. `table.clearPipeline().draw()`)
    $.fn.dataTable.Api.register('clearPipeline()', function() {
        return this.iterator('table', function(settings) {
            settings.clearCache = true;
        });
    });

    var delay = (function(){
        var timer = 0;
        return function(callback, ms){
          clearTimeout (timer);
          timer = setTimeout(callback, ms);
        };
    })();

    var asInitVals = new Array();

    var results = $("#result_list").DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": $.fn.dataTable.pipeline({
            "url": "data/",
            "pages": 5,
            "data": function(d) {
                $.each(d.columns, function(key, obj){
                    if (obj.name in $.urlVars) {
                        obj.search.value = $.urlVars[obj.name];
                    }
                });
                d.owner_filter = (('mine' in $.urlVars) ? $.urlVars['mine'] : $.cookie('owner_filter'));
                d.search_filter = (('q' in $.urlVars) ? $.urlVars['q'] : $.cookie('search_filter'));
                // We do this to work with the data better.
                d.json_data = JSON.stringify(d);
            }
            //type: "POST"
        }),
        "paging": true,
        "lengthMenu": [10, 25, 50],
        "paginationType": "full_numbers",
        "autoWidth": false,
        "stateSave": true,
        "dom": '<"header well well-sm"r>t<"paginator well well-sm"lpi<"clear">>',
        "order": [[ 1, "asc" ]],
        "language": {
            "lengthMenu": "Show _MENU_ records",
            "search": ""
        },
        "stateLoaded": function (settings, data) {
            //$("#s_host").val(('hostname' in $.urlVars) ? $.urlVars['hostname'] : data.aoSearchCols[1].sSearch);
            $("#s_host").val(data.aoSearchCols[1].sSearch);
            $("#s_mac").val(data.aoSearchCols[2].sSearch);
            $("#s_ip").val(data.aoSearchCols[3].sSearch);
            $("#s_expires").val(data.aoSearchCols[4].sSearch);
        },
        "columns": [
            { "name": "select", "orderable": false, "searchable": false  },
            { "name": "hostname", "orderable": true },
            { "name": "mac", "orderable": true },
            { "name": "ip_address", "orderable": false },
            { "name": "expires", "orderable": true },
            { "name": "mac_last_seen", "orderable": false, "searchable": false  },
            { "name": "ip_last_seen", "orderable": false, "searchable": false  },
            { "name": "dns_records", "orderable": false, "searchable": false  },
            { "name": "edit", "orderable": false, "searchable": false  },
        ],
        "drawCallback": function(settings) {
            $("#result_list span.flagged").parents('tr').addClass('flagged')

            // Set pagination to stick when scrolling
            var page_bar = $('.paginator')
            page_bar.removeClass('fixed')
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
        },
        "infoCallback": function(settings, start, end, max, total, pre) {
            if (total < max){
                $("#filtered-label").show();
                $(".search_init, #id_search").each(function(){
                    if ($(this).val() != '') {
                        $(this).addClass('red-highlight');
                    }
                });
                return "Showing " + start + " to " + end + " of " + total + " entries (filtered from " + max + " total entries)"
            }
            else {
                $("#filtered-label").hide();
                return "Showing " + start + " to " + end + " of " + total + " entries"
            }
        }
    }).columns.adjust();

    var pageOnchange = function() {
        var s=(document.body.scrollTop||document.documentElement.scrollTop) + window.innerHeight;
        if(s<height){page_bar.addClass('fixed');}
        else{page_bar.removeClass('fixed');}
    }

    $('#id_search').yourlabsAutocomplete({
        url: '/api/web/IPAMSearchAutoComplete',
        choiceSelector: '[data-value]',
        minimumCharacters: 2,
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

    $('#id_search').on('keyup selectChoice', function(){
        var value = $(this).val() ? $(this).val() : '';
        console.log('hi');
        delay(function(){
            $.cookie('search_filter', value, {expires: 1, path: '/hosts/'});
            results.clearPipeline().draw();
        }, 300);
    });

    $('#changelist-form').on('keyup keypress', function(e) {
      var code = e.keyCode || e.which;
      if (code  == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#changelist-filters-toggle").on('click', function() {
        $("#changelist-filter-actions").toggle();
        $(this).toggleClass('btn-inverse');
    });

    //Triger filtering on owners
    $("#filter-owners button").on('click', function() {
        if (!$(this).hasClass('active')) {
            $("#filter-owners button").removeClass('btn-primary');
            $(this).addClass('btn-primary');
            $.cookie('owner_filter', $(this).val(), {expires: 1, path: '/hosts/'});
            results.clearPipeline().draw();
            $(this).blur();
        }
    });

    $("#result_list").on('click', '.host-details', function() {
        var a = $(this);
        var tr = $(this).parents('tr')[0];
        var row = results.row(tr);
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
                    a.find('span').removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down');
                    row.child(data, 'host-detail').show();
                }
            });
        }
        return false;
    })

    // JS Styling :/
    $("div.header").append($("#actions"));
    $("#actions").append($("#result_list_processing")).append('<div class="clear"><!-- --></div>');
    $("#search-help-button").after($("#result_list_filter"));
    $("#result_list_filter input").prop('placeholder', 'Quick Search');

    // Clear all filters logic
    $("#clear-filters").on('click', function(e) {
        if ($.isEmptyObject($.urlVars)) {
            $.removeCookie('search_filter', {path: '/hosts/'});

            $(".search_init").val('');
            $("#id_search").val('');
            $(".search_init, #id_search").removeClass('red-highlight');

            results.clearPipeline().columns().search('').draw();
        }
    });

    $(".search_init").on('input', function(e) {
        /* Filter on the column (the index) of this element */
        var self = this;
        delay(function(){
            results.column($(self).attr('rel')).search($(self).val()).draw();
        }, 300);
    });

    $(".filter_init").on('change', function(e) {
        /* Filter on the column (the index) of this element */
        var self = this;
        delay(function(){
            results.column($(self).attr('rel')).search($(self).val()).draw();
        }, 300);
    });

    $(".help-button").on('click', function(){
        $(this).next('div').toggle();
    });

    $(".help-close").on('click', function(){
        $(this).parent('div').hide();
    });

    $("#search-help-button").on('click', function(){
        $("#search-help").toggle();
        return false;
    });

    $("#search-info-close").on('click', function() {
        $("#search-help").hide();
    });

    // Toggle all select for checkboxes
    $("#action-toggle").on('click', function() {
        if ($(this).is(":checked")) {
            $(".action-select").prop('checked', 'checked');
        }
        else {
            $(".action-select").prop('checked', '');
        }
    });

    // Action submit logic
    $("#action-submit").on('click', function() {
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
