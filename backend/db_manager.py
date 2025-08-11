#!/usr/bin/env python3
"""
Database management utility for SMS Chat application.
Provides commands for setting up, migrating, and resetting databases.
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import argparse

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url or not self.database_url.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be set to a PostgreSQL connection string")
        
        self.parse_postgres_url()
    
    def parse_postgres_url(self):
        """Parse PostgreSQL URL into components"""
        # postgresql://user:password@host:port/database
        url_parts = self.database_url.replace("postgresql://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_port_db = url_parts[1].split("/")
        host_port = host_port_db[0].split(":")
        
        self.db_user = user_pass[0]
        self.db_password = user_pass[1]
        self.db_host = host_port[0]
        self.db_port = host_port[1] if len(host_port) > 1 else "5432"
        self.db_name = host_port_db[1]
    
    def check_postgres_connection(self):
        """Check if PostgreSQL is running and accessible"""
            
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user="postgres",
                password="",
                database="postgres"
            )
            conn.close()
            return True
        except psycopg2.Error:
            return False
    
    def setup_postgres(self):
        """Set up PostgreSQL database and user"""
        
        print(f"Setting up PostgreSQL database: {self.db_name}")
        print(f"Host: {self.db_host}:{self.db_port}")
        print(f"User: {self.db_user}")
        
        try:
            # Try to connect with different superuser credentials
            try:
                postgres_password = input("Enter PostgreSQL superuser (postgres) password (press Enter if no password): ")
                if not postgres_password:
                    postgres_password = None
            except (EOFError, KeyboardInterrupt):
                print("\nTrying with default password 'postgres'...")
                postgres_password = "postgres"
            
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user="postgres",
                password=postgres_password,
                database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Create user if not exists
            cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (self.db_user,))
            if not cursor.fetchone():
                cursor.execute(
                    sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(self.db_user)),
                    (self.db_password,)
                )
                print(f"✅ Created user: {self.db_user}")
            else:
                print(f"✅ User {self.db_user} already exists")
            
            # Create database if not exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            if not cursor.fetchone():
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(self.db_name),
                        sql.Identifier(self.db_user)
                    )
                )
                print(f"✅ Created database: {self.db_name}")
            else:
                print(f"✅ Database {self.db_name} already exists")
            
            # Grant privileges
            cursor.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    sql.Identifier(self.db_name),
                    sql.Identifier(self.db_user)
                )
            )
            print(f"✅ Granted privileges to {self.db_user}")
            
            cursor.close()
            conn.close()
            
            print("\n🎉 PostgreSQL setup complete!")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Error setting up PostgreSQL: {e}")
            return False
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled")
            return False
    
    def run_migrations(self):
        """Run Alembic migrations"""
        print("Running database migrations...")
        try:
            result = subprocess.run(["alembic", "upgrade", "head"], 
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                print("✅ Migrations completed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Migration failed:")
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("❌ Alembic not found. Make sure it's installed: pip install alembic")
            return False
    
    def create_migration(self, message):
        """Create a new migration"""
        print(f"Creating migration: {message}")
        try:
            result = subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], 
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                print("✅ Migration created successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Migration creation failed:")
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("❌ Alembic not found. Make sure it's installed: pip install alembic")
            return False
    
    def reset_database(self):
        """Reset database (drop and recreate)"""
        
        print(f"⚠️  WARNING: This will DROP and recreate database '{self.db_name}'")
        try:
            confirm = input("Are you sure? Type 'yes' to confirm: ")
            if confirm.lower() != 'yes':
                print("❌ Reset cancelled")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Auto-confirming database reset (likely running in automated mode)")
            # Auto-confirm for automated/test scenarios
        
        try:
            try:
                postgres_password = input("Enter PostgreSQL superuser (postgres) password: ")
            except (EOFError, KeyboardInterrupt):
                print("\nUsing default password 'postgres'...")
                postgres_password = "postgres"
            
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user="postgres",
                password=postgres_password,
                database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Terminate connections to the database
            cursor.execute("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
            """, (self.db_name,))
            
            # Drop and recreate database
            cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.db_name)))
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(self.db_name),
                    sql.Identifier(self.db_user)
                )
            )
            
            cursor.close()
            conn.close()
            
            print(f"✅ Database {self.db_name} reset successfully")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Error resetting database: {e}")
            return False
    
    def seed_data(self):
        """Run the seed data script"""
        print("Seeding database with demo data...")
        try:
            result = subprocess.run([sys.executable, "seed_demo_data.py"], 
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                print("✅ Demo data seeded successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Seeding failed:")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error running seed script: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Database management utility")
    parser.add_argument("command", choices=[
        "setup", "migrate", "reset", "seed", "create-migration", "full-setup"
    ], help="Command to run")
    parser.add_argument("-m", "--message", help="Migration message (for create-migration)")
    
    args = parser.parse_args()
    
    db = DatabaseManager()
    
    if args.command == "setup":
        success = db.setup_postgres()
        sys.exit(0 if success else 1)
    
    elif args.command == "migrate":
        success = db.run_migrations()
        sys.exit(0 if success else 1)
    
    elif args.command == "reset":
        success = db.reset_database()
        sys.exit(0 if success else 1)
    
    elif args.command == "seed":
        success = db.seed_data()
        sys.exit(0 if success else 1)
    
    elif args.command == "create-migration":
        if not args.message:
            print("❌ Migration message required. Use -m 'message'")
            sys.exit(1)
        success = db.create_migration(args.message)
        sys.exit(0 if success else 1)
    
    elif args.command == "full-setup":
        print("🚀 Running full database setup...")
        steps = [
            ("Setting up PostgreSQL", lambda: db.setup_postgres()),
            ("Running migrations", lambda: db.run_migrations()),
            ("Seeding demo data", lambda: db.seed_data())
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Failed at: {step_name}")
                sys.exit(1)
        
        print("\n🎉 Full setup completed successfully!")
        print("Your database is ready to use!")

if __name__ == "__main__":
    main()