# PostgreSql webhook

## Getting started

### 1) Set up the triggers:

We need to setup triggers on the tables that we we are interested in. Create a `triggers.json` file (see [sample.triggers.json](sample.triggers.json)) with the required tables and events.

Note: This command requires `python3`.

```bash
$ ./gen-triggers.py triggers.json | psql -h localhost -p 5432 -U postgres -d postgres --single-transaction --

# teste local
./gen-triggers.py test.triggers.json | psql -h localhost -p 27017 -U dev -d sistema --single-transaction --
```

### 2) Run postgres-webhook:

Run the postgres-webhook Docker image (that has the `postgres-webhook` binary baked in):

```bash
$ docker run \
    -e DBNAME="postgres" \
    -e PGUSER="postgres" \
    -e PGPASS="''" \
    -e PGHOST="localhost" \
    -e PGPORT=5432 \
    -e WEBHOOKURL="http://localhost:5000/" \
    --net host \
    -it postgres-webhook:v0.0.1
```

Or using docker-compose, see (file [docker-compose.yml](docker-compose.yml))

```bash
docker-compose up -d --build
```

## Examples

### INSERT

Query:

```sql
INSERT INTO test_table(name) VALUES ('abc1');
```

JSON webhook payload:

```json
{ "data": { "id": 1, "name": "abc1" }, "table": "test_table", "op": "INSERT" }
```

### UPDATE

Query:

```sql
UPDATE test_table SET name = 'pqr1' WHERE id = 1;
```

JSON webhook payload:

```json
{ "data": { "id": 1, "name": "pqr1" }, "table": "test_table", "op": "UPDATE" }
```

### DELETE

Query:

```sql
DELETE FROM test_table WHERE id = 1;
```

JSON webhook payload:

````json
{"data": {"id": 1, "name": "pqr1"}, "table": "test_table", "op": "DELETE"}

## Desinstalando rotinas de notificação

To remove the postgres-webhook related functions and triggers that were added to Postgres, run this in psql:

```bash
psql -h localhost -p 27017 -U dev -d sistema
````

```sql
DO $$DECLARE r record;
BEGIN
    FOR r IN SELECT routine_schema, routine_name FROM information_schema.routines
             WHERE routine_name LIKE 'notify_postgres_webhook%'
    LOOP
        EXECUTE 'DROP FUNCTION ' || quote_ident(r.routine_schema) || '.' || quote_ident(r.routine_name) || ' CASCADE';
    END LOOP;
END$$;
```

## Build postgres-webhook:

### Requirements:

- PostgreSQL 9+
- `gcc`
- libcurl (`libcurl4-openssl-dev`)
- libppq (`libpq-dev`)

### Build:

```bash
$ make
```

### Run:

```bash
$ ./build/postgres-webhook 'host=localhost port=5432 dbname=postgres user=postgres password=' http://localhost:5000
```

## Test

1. Install the requirements specified in `tests/requirements.txt`
2. The tests assume that you have a local postgres instance at `localhost:5432` and a database called `postgres_webhook_test` which can be accessed by an `admin` user.
3. Run postgres-webhook on this database with the webhook url set to `http://localhost:5000`
4. run `run_tests.sh` script in the `tests` directory.
