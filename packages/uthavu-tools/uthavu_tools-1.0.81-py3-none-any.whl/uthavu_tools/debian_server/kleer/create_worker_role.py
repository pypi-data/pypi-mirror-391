import psycopg2
from psycopg2 import sql

# --- Configuration ---
DB_NAME = "demo"             # existing local DB
ADMIN_USER = "postgres"                  # superuser for connection
ADMIN_PASS = "password"  # replace with your password
WORKER_USER = "worker"
WORKER_PASS = "2dePvdJc*QpdmR}ga"        # from your docker-compose.yml

# --- Script Logic ---
def create_worker_role():
    print("👷 Ensuring 'worker' role exists...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=ADMIN_USER,
        password=ADMIN_PASS,
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Check if worker role exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", [WORKER_USER])
    exists = cur.fetchone()

    if not exists:
        print("➡️  Creating role 'worker'...")
        cur.execute(sql.SQL("""
            CREATE ROLE {user} WITH
                LOGIN
                NOSUPERUSER
                INHERIT
                NOCREATEDB
                NOCREATEROLE
                NOREPLICATION
                ENCRYPTED PASSWORD %s;
        """).format(user=sql.Identifier(WORKER_USER)), [WORKER_PASS])
        print("✅ Role 'worker' created.")
    else:
        print("ℹ️  Role 'worker' already exists — skipping creation.")

    cur.close()
    conn.close()
    print("🎉 Done! 'worker' user is now available in your local PostgreSQL.")

if __name__ == "__main__":
    create_worker_role()
