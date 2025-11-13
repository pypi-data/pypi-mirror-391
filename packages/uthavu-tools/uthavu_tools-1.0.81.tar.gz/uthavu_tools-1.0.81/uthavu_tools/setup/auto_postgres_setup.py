import subprocess
import psycopg2
import time
from psycopg2 import sql

# --- Configuration ---
PG_USER = "postgres"
PG_PASSWORD = "password"
PG_HOST = "localhost"
PG_PORT = "5432"
DB_NAME = "kleer_local_2"
DUMP_PATH = r"C:\Users\Jawahar\Downloads\bya_backup_20251031_002814.sql"


def run_command(cmd):
    """Run a shell command and stream output."""
    print(f"\n⚙️  Running: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line.strip())
    process.wait()
    if process.returncode != 0:
        print(process.stderr.read())
        raise Exception(f"❌ Command failed with code {process.returncode}")


def create_database():
    """Create the database if it doesn’t exist."""
    print(f"\n🧱 Creating database '{DB_NAME}' ...")
    try:
        conn = psycopg2.connect(
            dbname="postgres", user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [DB_NAME]
        )
        exists = cur.fetchone()
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"✅ Database '{DB_NAME}' created.")
        else:
            print(f"ℹ️  Database '{DB_NAME}' already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Error creating database:", e)


def restore_database():
    """Restore the dump into the database."""
    print(f"\n📦 Restoring dump from {DUMP_PATH} ...")
    PSQL_PATH = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"  # ✅ full path
    cmd = f'"{PSQL_PATH}" -U {PG_USER} -d {DB_NAME} -f "{DUMP_PATH}"'
    run_command(cmd)
    print("✅ Restore completed.")


def verify_tables():
    """Connect to the DB and list all tables."""
    print("\n🔍 Verifying tables ...")
    conn = psycopg2.connect(
        dbname=DB_NAME, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)
    tables = cur.fetchall()
    print(f"✅ Found {len(tables)} table(s):")
    for schema, name in tables:
        print(f"  - {schema}.{name}")

    # Optional: show sample rows from first table
    if tables:
        cur.execute(sql.SQL("SELECT * FROM {} LIMIT 5").format(sql.Identifier(tables[0][1])))
        rows = cur.fetchall()
        print(f"\n📄 Sample data from {tables[0][1]}:")
        for row in rows:
            print(row)

    cur.close()
    conn.close()


def main():
    print("🚀 Starting PostgreSQL automation script ...")

    create_database()
    time.sleep(1)
    restore_database()
    verify_tables()

    print("\n🎉 Done! Your database is fully set up and verified.")


if __name__ == "__main__":
    main()
