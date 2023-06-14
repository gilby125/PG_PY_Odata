this code turns a Postgres table into an Odata endpoint.

run example: 
    python app.py --db_connection "postgresql://user:password@host:port/database" --table_name "table1,table2"

http://127.0.0.1:5000/odata/{table_name}