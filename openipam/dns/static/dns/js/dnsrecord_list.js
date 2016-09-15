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

    var results = $("#result_list").DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": $.fn.dataTable.pipeline({
            "url": "/dns/data/",
            "pages": 5,
            "data": function(d) {
                if (!$.isEmptyObject($.urlVars)) {
                    $.each(d.columns, function(key, obj){
                        obj.search.value = (obj.name in $.urlVars) ? $.urlVars[obj.name] : '';
                    })
                    d.change_filter = ('mine' in $.urlVars) ? $.urlVars['mine'] : '';
                    d.search_filter = ('q' in $.urlVars) ? $.urlVars['q'] : '';

                }
                else {
                    d.change_filter = $.cookie('change_filter');
                    d.search_filter = $.cookie('search_filter');
                }

                // We do this to work with the data better.
                d.json_data = JSON.stringify(d);
            }
            //type: "POST"
        }),
        "paging": true,
        "paginationType": "full_numbers",
        "lengthMenu": [10, 25, 50],
        "autoWidth": false,
        "stateSave": true,
        "dom": '<"header well well-sm"r>t<"paginator well well-sm"lpi<"clear">>',
        "order": [[ 1, "asc" ]],
        "language": {
            "lengthMenu": "Show _MENU_ records",
            "search": ""
        },
        "stateLoaded": function (settings, data) {
            console.log(data.columns[1]);
            $("#name-search").val(data.columns[1].search.search);
            $("#type-filter").val(data.columns[3].search.search);
            $("#content-search").val(data.columns[4].search.search);
        },
        "columns": [
            { "name": "select", "orderable": false, "searchable": false  },
            { "name": "name", "orderable": true },
            { "name": "ttl", "orderable": false, "searchable": false },
            { "name": "ttl", "orderable": true },
            { "name": "content", "orderable": true },
            { "name": "host", "orderable": false, "searchable": false  },
            { "name": "view", "orderable": false, "searchable": false  },
            { "name": "edit", "orderable": false, "searchable": false  },
        ],
        "initComplete": function() {

        },
        "drawCallback": function(settings) {
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

            formActionCheck();
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
    }).columns.adjust();;

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

    $('#id_search').on('input selectChoice', function(){
        var value = $(this).val() ? $(this).val() : '';

        delay(function(){
            $.cookie('search_filter', value, {expires: 1, path: '/dns/'});
            results.clearPipeline().draw();
        }, 300);
    });

    $('#changelist-form').on("keyup keypress", function(e) {
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
        var newRow = thisRow.clone().find("input").val('').end().find('.dns-ttl').val('14400').end();
        thisRow.removeClass("extra").find("a.add-record").remove().end().find("a.remove-record").show();
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
    $("a.edit-all").on('click', function() {
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
    $("#cancel-edit").on('click', function() {
        $("a.cancel-dns").click();
        $("#form-actions").hide();
        $("#action-toggle").removeAttr('checked');
        $('.add-row:not(.extra)').remove();
        $('.add-row.extra').find('input').val('').end().find('.dns-ttl').val('14400');
    });


    $("#changelist-filters-toggle").on('click', function() {
        $("#changelist-filter-actions").toggle();
        $(this).toggleClass('btn-inverse');
    });


    $("#filter-close").on('click', function() {
        $("#changelist-filters-toggle").click();
    });

    //Triger filtering on change perms
    $("#filter-change button").on('click', function() {
        if (!$(this).hasClass('btn-primary')) {
            $.cookie('change_filter', $(this).val(), {expires: 1, path: '/dns/'});

            if ($.isEmptyObject($.urlVars)) {
                $("#filter-change button").removeClass('btn-primary');
                $(this).addClass('btn-primary');
                results.clearPipeline().draw();
                $(this).blur();
            }
            else {
                location.href = '/dns/';
            }
        }
    });

    // JS Styling :/
    $("div.header").append($("#actions"));
    $("#actions").append($("#result_list_processing")).append('<div class="clear"><!-- --></div>');
    $("#search-help-button").after($("#result_list_filter"));
    $("#result_list_filter input").prop('placeholder', 'Quick Search');
    //$("#changelist-search").prepend($("#result_list_length"));

    //$(".pagination").append("<div style='clear: both;'><!-- --></div>").append($("#form-actions").show());
    $(".paginator").prepend($("#form-actions"));
    $(".paginator").append("<div style='clear: both;'><!-- --></div>");

    // Clear all filters logic
    $("#clear-filters").on('click', function(e) {
        if ($.isEmptyObject($.urlVars)) {
            $.removeCookie('search_filter', {path: '/dns/'});

            $(".search_init").val('');
            $("#id_search").val('');
            $(".search_init, #id_search").removeClass('red-highlight');

            results.clearPipeline().columns().search('').draw();
        }
    });

    $(".search_init").on('input', function() {
        var self = this;
        delay(function(){
            results.column($(self).attr('rel')).search($(self).val()).draw();
        }, 300);
    });

    $(".filter_init").on('change', function() {
        /* Filter on the column (the index) of this element */
        var self = this;
        delay(function(){
            results.column($(self).attr('rel')).search($(self).val()).draw();
        }, 300);

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
    $("#action-submit").on('click', function() {
        var action = $("#dns-action").val();
        var records = $(".action-select:checked");

        if (records.length > 0) {
            if (action == 'delete') {
                var res = confirm("Are you sure you want to delete the selected dns records?")
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
