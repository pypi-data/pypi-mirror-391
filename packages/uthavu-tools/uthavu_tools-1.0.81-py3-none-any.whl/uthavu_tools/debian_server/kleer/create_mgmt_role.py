import psycopg2
from psycopg2 import sql

# --- Configuration ---
DB_NAME = "demo"            # your existing local DB
ADMIN_USER = "postgres"                 # superuser for connection
ADMIN_PASS = "password"  # replace with your password
MGMT_USER = "mgmt"
MGMT_PASS = "kWA&s@PTOt-L,E#w@x"        # same as your Docker env

# --- Script Logic ---
def create_mgmt_role():
    print("👤 Ensuring 'mgmt' role exists and has privileges...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=ADMIN_USER,
        password=ADMIN_PASS,
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Check if mgmt role exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", [MGMT_USER])
    exists = cur.fetchone()

    if not exists:
        print("➡️  Creating role 'mgmt'...")
        cur.execute(sql.SQL("""
            CREATE ROLE {user} WITH
                LOGIN
                NOSUPERUSER
                INHERIT
                NOCREATEDB
                CREATEROLE
                NOREPLICATION
                ENCRYPTED PASSWORD %s;
        """).format(user=sql.Identifier(MGMT_USER)), [MGMT_PASS])
        print("✅ Role 'mgmt' created.")
    else:
        print("ℹ️  Role 'mgmt' already exists, updating privileges...")

    # Apply grants and ownership changes
    print("🔐 Applying privileges...")
    cur.execute(sql.SQL("""
        GRANT ALL PRIVILEGES ON DATABASE {db} TO {user};
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {user};
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {user};
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO {user};
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO {user};
        ALTER SCHEMA public OWNER TO {user};
    """).format(db=sql.Identifier(DB_NAME), user=sql.Identifier(MGMT_USER)))

    print("✅ 'mgmt' role privileges and schema ownership updated.")
    cur.close()
    conn.close()
    print("🎉 Done! 'mgmt' user is now fully active and has all required privileges.")

if __name__ == "__main__":
    create_mgmt_role()
