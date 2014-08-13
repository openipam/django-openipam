from django.db import connection

hack_sql = r"""SELECT 'ALTER TABLE '||pgn.nspname||'.'||tbl.relname||' DROP CONSTRAINT '||cons.conname||E';\n'
        || 'ALTER TABLE '||pgn.nspname||'.'||tbl.relname||' ADD CONSTRAINT '||cons.conname||' '
        || regexp_replace(pg_get_constraintdef(cons.oid, true), '( DEFERRABLE|$)', ' ON UPDATE CASCADE ON DELETE SET NULL\1') || ';'
FROM pg_constraint cons
  JOIN pg_class tbl ON cons.conrelid = tbl.oid
  JOIN pg_namespace pgn ON pgn.oid = tbl.relnamespace
WHERE contype = 'f'
    AND pg_get_constraintdef(cons.oid, true) LIKE '% {referenced_table}({referenced_column}) %'
    AND tbl.relname = '{table}';"""

def update_fkey_sql(table, referenced_table, referenced_column, on_update='RESTRICT', on_delete='RESTRICT'):
    return hack_sql.format(
                           table=table,
                           referenced_table=referenced_table,
                           referenced_column=referenced_column,
                           onclause='ON UPDATE {} ON DELETE {}'.format(on_update, on_delete),
                          )

def get_sql(table, referenced_table, referenced_column, on_update='RESTRICT', on_delete='RESTRICT'):
    curs = connection.cursor()
    print 'get_sql()'
    sql_gen_query = update_fkey_sql(table, referenced_table, referenced_column, on_update=on_update, on_delete=on_delete)
    print '    execute({})'.format(sql_gen_query)
    curs.execute(sql_gen_query)
    sql = '\n'.join([i[0] for i in curs.fetchall()])
    print sql
    return sql

