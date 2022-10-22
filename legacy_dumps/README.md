### Create a database dump

`docker-compose exec postgres bash`
`pg_dump -U postgres -d postgres -f dump.txt`
`docker cp seeder_postgres_1:/dump.txt ./legacy_dumps/`

### Drop all tables in the schema

Source: https://stackoverflow.com/questions/3327312/how-can-i-drop-all-the-tables-in-a-postgresql-database

`docker-compose exec postgres bash`
`psql -U postgres`

```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

### Then import the text file using psql

`docker cp dump.txt seeder_postgres_1:/`
`docker-compose exec postgres bash`
`psql -U postgres < dump.txt`
