#!/usr/bin/env python3

import argparse
import json

dropPrevTriggers = """
DO $$DECLARE r record;
BEGIN
    FOR r IN SELECT routine_schema, routine_name FROM information_schema.routines
             WHERE routine_name LIKE 'notify_postgres_webhook%'
    LOOP
        EXECUTE 'DROP FUNCTION ' || quote_ident(r.routine_schema) || '.' || quote_ident(r.routine_name) || '() CASCADE';
    END LOOP;
END$$;
"""

functionTemplate = """
CREATE OR REPLACE FUNCTION {schema}.notify_postgres_webhook_{table}_{event}() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  DECLARE
    notification text;
    cur_rec record;
    BEGIN
      -- Build the notification
      notification := ''
              || '{{'
              || '"op":"'        || TG_OP                                || '",'
              || '"schema":"'    || TG_TABLE_SCHEMA                      || '",'
              || '"table":"'     || TG_TABLE_NAME                        || '",'
              || '"data":'       || {data_expression}                    || ''
              || '}}';

      PERFORM pg_notify('postgres_webhook', notification);
      RETURN cur_rec;
    END;
$$;
DROP TRIGGER IF EXISTS notify_postgres_webhook_{table}_{event} ON {schema}.{table};
CREATE TRIGGER notify_postgres_webhook_{table}_{event} AFTER {event} ON {schema}.{table} FOR EACH ROW EXECUTE PROCEDURE {schema}.notify_postgres_webhook_{table}_{event}();
"""

def genSQL(tableConf):
    table = tableConf["table"]
    schema = tableConf.get("schema", "public")
    columns = tableConf.get("columns", "*")
    triggerConf = {}
    if type(columns) == dict:
        triggerConf = columns
    else:
        triggerConf['insert'] = columns
        triggerConf['update'] = columns
        triggerConf['delete'] = columns
    for op, columns in triggerConf.items():
        opL = op.lower()
        if opL == 'delete':
            recVar = 'OLD'
        else:
            recVar = 'NEW'
        if columns == "*":
            dataExp = "row_to_json({})".format(recVar)
        else:
            dataExp = "row_to_json((select r from (SELECT {}) as r))".format(
                ",".join(["{}.{}".format(recVar, col) for col in columns])
            )
        sql = functionTemplate.format(
            schema=schema,
            table=table,
            event=opL,
            data_expression=dataExp
        )
        print(sql)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'conf',
        help="The JSON configuration for generating triggers (see sample.triggers.json)",
        type=argparse.FileType('r')
    )
    args = parser.parse_args()
    print(dropPrevTriggers)
    for conf in json.load(args.conf):
        genSQL(conf)
