"""
Django Middleware for SQL Debugging
===================================

These are a set of middlewares that provide SQL debugging for your Django app.

The following middlewares are included:

    * SQLLogToConsoleMiddleware
    * SQLLogToConsoleColorMiddleware
    * SQLLogMiddlewareSimple
    * SQLLogMiddleware

SQLLogToConsoleMiddleware
-------------------------

This middleware provides SQL query output to the console.  This is usefull
when you are using the built in development server.

SQLLogToConsoleColorMiddleware
------------------------------

Same as SQLLogToConsoleMiddleware except prints in color for queries that are
slow or bothersome.  Note: Colors are set for terminals that have light
backgrounds.

SQLLogMiddlewareSimple
----------------------

Prints a basic html dump of queries run in your django template.


SQLLogMiddlewareSimple
----------------------

Same as SQLLogMiddlewareSimple except works with ajax requests and
has a nicer output.

"""

from django.db import connections, connection
from django.template import Template, Context
from django.conf import settings
import sys
import re
import os
import time
import datetime


class SQLLogToConsoleMiddleware(object):
    def process_response(self, request, response):
        if settings.DEBUG:
            for connection_name in connections:
                conn = connections[connection_name]
                if conn.queries:
                    qtime = sum([float(q['time']) for q in conn.queries])
                    header_t = Template("{{name}}: {{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds")
                    print header_t.render(Context({
                                          'name': connection_name,
                                          'sqllog': conn.queries,
                                          'count': len(conn.queries),
                                          'time': qtime
                                          }))
                    t = Template("{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
                print t.render(Context({'sqllog': conn.queries}))
        return response


class SQLLogToConsoleColorMiddleware:
    """
    Color SQL logging middleware.
    Prints a short summary (number of database queries and
    total time) for each request. Additionally it will print
    the raw SQL if any of the configurable thresholds are
    exceeded, in order to draw your attention to pages
    that trigger slow or too many queries.

    The available tresholds are:
        * Query count
        * Total Time (for all SQL queries)
        * Query Time (for individual SQL queries)

    We're trying to keep the output readable by modest use of ANSI color.


    **Example output**


    This is what you get for normal page views where
    no treshold was exceeded::

        0.006s | 3 queries

    This is what you get for page views where one or more
    tresholds have been exceeded. Please note that in reality the
    SQL is *not* truncated. I did that by hand to keep this comment
    readable::

        SELECT "django_session"."session_key","django_session"."session_data",
        FROM "django_session"
        WHERE ("django_session"."session_key" = '6495c82cf81b34dc0c4dbb91fc641

        SELECT "core_userprofile"."id","core_userprofile"."user_id","core_user
        FROM "core_userprofile" INNER JOIN "auth_user" AS "core_userprofile__u
        WHERE ("core_userprofile__user"."username" = 'sook')

        SELECT "auth_user"."id","auth_user"."username","auth_user"."first_name
        f","auth_user"."is_active","auth_user"."is_superuser","auth_user"."las
        FROM "auth_user"
        WHERE ("auth_user"."id" = 55)

        SELECT "auth_user"."id","auth_user"."username","auth_user"."first_name
        f","auth_user"."is_active","auth_user"."is_superuser","auth_user"."las
        FROM "auth_user"
        WHERE ("auth_user"."id" = 55)

        SELECT "auth_message"."id","auth_message"."user_id","auth_message"."me
        FROM "auth_message"
        WHERE ("auth_message"."user_id" = 55)

        0.176s | 5 queries


    **Installation**


    Edit your settings.py to enable the middleware::

        MIDDLEWARE_CLASSES = (
            'djangopad.middleware.sql_log.SQLLogToConsoleColorMiddleware',
            ...
        )

    Finally you may tweak the various options in
    settings.py, see below.


    **Options in settings.py (with defaults)**::


        LOG_COLORSQL_ENABLE = True #(boolean)

        #True  == Enable the middleware #(default)
        #False == Disable the middleware, nothing will be printed

        LOG_COLORSQL_VERBOSE = False #(boolean)

        #True  == The SQL will always be printed.
        #False == The SQL will only be printed if one of the tresholds is
                 exceeded

        LOG_COLORSQL_WARN_TOTALTIME = 0.5 #(float)

        #If the total time for all db queries exceeds
        #this value (in seconds) then the SQL will
        #be printed and the measured time in the summary-
        #line will be printed in YELLOW.

        LOG_COLORSQL_ALERT_TOTALTIME = 1.0 #(float)

        #If the total time for all db queries exceeds
        #this value (in seconds) then the SQL will
        #be printed and the measured time in the summary-
        #line will be printed in RED.

        LOG_COLORSQL_WARN_TOTALCOUNT = 6 #(integer)

        #If the number of db queries exceeds this value
        #then the SQL will be printed and the query-count
        #in the summary line will be printed in YELLOW.

        LOG_COLORSQL_ALERT_TOTALCOUNT = 10 #(integer)

        #If the number of db queries exceeds this value
        #then the SQL will be printed and the query-count
        #in the summary line will be printed in RED.

        LOG_COLORSQL_WARN_TIME = 0.05 #(float)

        #If the time for any individual db query exceeds
        #this value (in seconds) then the SQL will be
        #printed and the offending query be highlighted
        #in YELLOW.

        LOG_COLORSQL_ALERT_TIME = 0.20 #(float)

        #If the time for any individual db query exceeds
        #this value (in seconds) then the SQL will be
        #printed and the offending query be highlighted
        #in RED.

    """

    def process_response(self, request, response):
        from django.conf import settings
        enable = getattr(settings, 'LOG_COLORSQL_ENABLE', True)

        if False == enable:
            return response

        verbose = getattr(settings, 'LOG_COLORSQL_VERBOSE', False)

        timewarn = getattr(settings, 'LOG_COLORSQL_WARN_TOTALTIME', 0.5)
        timealert = getattr(settings, 'LOG_COLORSQL_ALERT_TOTALTIME', 1.0)

        countwarn = getattr(settings, 'LOG_COLORSQL_WARN_TOTALCOUNT', 6)
        countalert = getattr(settings, 'LOG_COLORSQL_ALERT_TOTALCOUNT', 10)

        qtimewarn = getattr(settings, 'LOG_COLORSQL_WARN_TIME', 0.05)
        qtimealert = getattr(settings, 'LOG_COLORSQL_ALERT_TIME', 0.20)

        # sanity checks...
        if qtimealert < qtimewarn:
            qtimewarn = qtimealert

        if countalert < countwarn:
            countwarn = countalert

        if timealert < timewarn:
            timewarn = timealert

        ttime = 0.0
        for q in connection.queries:
            qtime = float(q['time'])
            ttime = ttime + qtime
            if qtimewarn < qtime:
                verbose = True

        count = len(connection.queries)
        if timewarn <= ttime or countwarn <= count:
            verbose = True

        if verbose:
            print "\033[0;30;1m"
            print "-" * 70,
            print "\033[0m"

        i = 0
        for q in connection.queries:
            qtime = float(q['time'])

            if verbose or timewarn <= ttime or countwarn <= count:
                sql = q['sql']
                if sql:
                    sql = sql.replace(' FROM ', '\nFROM ').replace(' WHERE ', '\nWHERE ')

                tcolor = "\033[31m"
                ptime = "\033[7m %ss \033[0m" % (qtime)
                if qtimealert > qtime:
                    tcolor = "\033[33m"
                if qtimewarn > qtime:
                    tcolor = "\033[30;1m"
                    ptime = ""

                print "%s%s" % (tcolor, sql),
                print "%s\033[1m%s\033[0m" % (tcolor, ptime)
                i = i + 1
                if i < len(connection.queries):
                    print

        sys.stdout.write("\033[0;30;1m")
        print "-" * 70,
        print "\033[35;1m"

        qtime = ttime

        tcolor = "\033[31;1m"
        if timealert > qtime:
            tcolor = "\033[33;1m"
        if timewarn > qtime:
            tcolor = "\033[30;1m"

        ccolor = "\033[31;1m"
        if countalert > count:
            ccolor = "\033[33;1m"
        if countwarn > count:
            ccolor = "\033[30;1m"

        print "%s %.3fs \033[30;1m| %s%d queries\033[0m" % (tcolor, qtime, ccolor, count)
        sys.stdout.write("\033[0;30;1m")
        print "-" * 70,
        print "\033[0m"

        return response


class SQLLogMiddlewareSimple:
    def process_response(self, request, response):
        ttime = 0.0
        for q in connection.queries:
            ttime += float(q['time'])

        t = Template('''
            <div>
                <p><em>Total query count:</em> {{ count }}<br/>
                <em>Total execution time:</em> {{ time }}</p>
                <a href="#" class="sqllogbutton"><strong>SQL log: click to toggle</strong></a>
            </div>
            <div class="sqllog" style="display:none;">
                <ul class="sqllog">
                    {% for sql in sqllog %}
                        <li>{{ sql.time }}: {{ sql.sql }}</li>
                    {% endfor %}
                </ul>
            </div>
            <script type="text/javascript">
                /*<![CDATA[*/
                        if (typeof(jQuery) != 'undefined') {
                            jQuery("a.sqllogbutton").click(function(){
                                if (jQuery(this).parent().next().css('display', 'none')) {
                                    jQuery(this).parent().next().show();
                                }
                                else {
                                    jQuery(this).parent().next().hide();
                                }

                                return false;
                            });
                        }
                /*]]>*/
            </script>


        ''')
        response.content = "%s%s" % (response.content, t.render(Context({
                                     'sqllog': connection.queries,
                                     'count': len(connection.queries),
                                     'time': ttime})))
        return response


class SQLLogMiddleware:

    """
    Logs SQL statements and excecutions times to the end of templates.
    This works even with ajax requests.

    **settings.py**


    Make sure that the ``SQLLogMiddleware`` is in your ``MIDDLEWARE_CLASSES``. ::

        MIDDLEWARE_CLASSES = (
            'djangopad.middleware.sql_log.SQLLogMiddleware',
            ...
        )

    **Enable the middleware**


    In ``settings.py``::

        DEBUG_SQL = True

    """

    start = None

    def process_request(self, request):
        self.start = time.time()

    def process_response(self, request, response):
        # self.start is empty if an append slash redirect happened.
        debug_sql = getattr(settings, "DEBUG_SQL", False)
        if (not self.start) or not (settings.DEBUG and debug_sql):
            return response
        timesql = 0.0
        for q in connection.queries:
            timesql += float(q['time'])
            seen = {}
            duplicate = 0
        for q in connection.queries:
            sql = q["sql"]
            c = seen.get(sql, 0)
            if c:
                duplicate += 1
            q["seen"] = c
            seen[sql] = c + 1
        t = Template('''
            <fieldset class="sqlinfo" style="float:left; color: black; margin: 10px; background: #ffffcc; padding: 10px;">
                <h4>Django Query Execution</h4>
                <p>
                    <strong>request.path:</strong> {{ request.path|escape }}<br />
                    <strong>Total query count:</strong> {{ queries|length }}<br />
                    <strong>Total duplicate query count:</strong> {{ duplicate }}<br />
                    <strong>Total SQL execution time:</strong> {{ timesql }}<br />
                    <strong>Total Request execution time:</strong> {{ timerequest }}<br />
                </p>
                <a href="javascript:;" onclick="var data=this.parentNode.childNodes[7].innerHTML; var win = window.open('', 'SQLLogWindow', 'location=0,status=0,scrollbars=1,width=800,height=700'); win.document.write('<html><body>'+data+'</body></html>'); return false;"
                    style="color: blue;" class="sqllogbutton"><strong>Django SQL log for this page: click to toggle</strong></a>
                <div class="sqllog" style="display: none;">
                    <div>
                        {% if queries %}
                            <table border="1" cellspacing="1" cellpadding="3" style="font: 12px Arial;">
                                <tr>
                                    <th>Time</th>
                                    <th>Frequency</th>
                                    <th>SQL</th>
                                </tr>
                                {% for sql in queries %}
                                    <tr style="{% cycle 'background-color: #ffffe1;' 'background-color: #f4f4c8;' %}">
                                        <td align="center" valign="top">{{ sql.time }}</td>
                                        <td align="center" valign="top">{{ sql.seen }}</td>
                                        <td valign="top">{{ sql.sql }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No SQL queries for ths page.</p>
                        {% endif %}
                        {% if duplicate %}
                            <p class="dupl">To avoid duplicates, read: <a href="http://www.djangoproject.com/documentation/db-api/#caching-and-querysets" target="_blank">Caching and Querysets</a>.</p>
                        {% endif %}
                        <button class="sqlclose" onclick="javascript:window.close();">Close</button>
                    </div>
                </div>
            </fieldset>
        ''')
        timerequest = round(time.time() - self.start, 3)
        queries = connection.queries
        html = str(t.render(Context(locals())))
        if debug_sql is True:
            response.content = "%s%s" % (response.content, html)
            return response
        assert os.path.isdir(debug_sql), debug_sql
        outfile = os.path.join(debug_sql, "%s.html" % datetime.datetime.now().isoformat())
        fd = open(outfile, "wt")
        fd.write('''<html><head><title>SQL Log %s</title></head><body>%s</body></html>''' % (request.path, html))
        fd.close()
        return response
