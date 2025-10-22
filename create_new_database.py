#!/usr/bin/env python3
"""
Create a new database for fresh testing
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_new_database():
    """Create a new database for testing"""
    
    try:
        # Connect to postgres database to create new one
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/postgres')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("🆕 Creating New Database for Testing")
        print("=" * 50)
        
        # Database names
        new_db_name = 'pawnpro_test'
        original_db = 'pawnpro'
        
        print(f"📋 Plan:")
        print(f"   • Original DB: {original_db} (will be preserved)")
        print(f"   • New Test DB: {new_db_name} (will be created)")
        
        # Check if test database already exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (new_db_name,))
        exists = cur.fetchone()
        
        if exists:
            print(f"\n⚠️ Database '{new_db_name}' already exists!")
            choice = input(f"🤔 Do you want to drop and recreate it? (type 'YES' to confirm): ")
            
            if choice == 'YES':
                print(f"🗑️ Dropping existing database...")
                cur.execute(f"DROP DATABASE {new_db_name}")
                print(f"   ✅ Database dropped")
            else:
                print(f"❌ Operation cancelled")
                cur.close()
                conn.close()
                return
        
        # Create new database
        print(f"\n🆕 Creating new database '{new_db_name}'...")
        cur.execute(f"CREATE DATABASE {new_db_name}")
        print(f"   ✅ Database created successfully")
        
        cur.close()
        conn.close()
        
        # Copy schema and master data from original database
        print(f"\n📋 Copying schema and master data...")
        
        # Use pg_dump and pg_restore (requires PostgreSQL tools)
        import subprocess
        
        # Dump schema and data from original
        dump_command = [
            'pg_dump',
            '-h', 'localhost',
            '-U', 'postgres',
            '-d', original_db,
            '--schema-only',  # Only schema, no data
            '-f', f'{new_db_name}_schema.sql'
        ]
        
        try:
            result = subprocess.run(dump_command, capture_output=True, text=True, input='rnrinfo\n')
            if result.returncode == 0:
                print(f"   ✅ Schema exported")
                
                # Import schema to new database
                restore_command = [
                    'psql',
                    '-h', 'localhost',
                    '-U', 'postgres',
                    '-d', new_db_name,
                    '-f', f'{new_db_name}_schema.sql'
                ]
                
                result = subprocess.run(restore_command, capture_output=True, text=True, input='rnrinfo\n')
                if result.returncode == 0:
                    print(f"   ✅ Schema imported to new database")
                else:
                    print(f"   ❌ Schema import failed: {result.stderr}")
            else:
                print(f"   ❌ Schema export failed: {result.stderr}")
                
        except FileNotFoundError:
            print(f"   ⚠️ PostgreSQL command-line tools not found")
            print(f"   📝 You'll need to set up the schema manually")
        
        # Copy essential master data (accounts, companies, users)
        print(f"\n📊 Copying master data...")
        
        try:
            # Connect to both databases
            source_conn = psycopg2.connect(f'postgresql://postgres:rnrinfo@localhost:5432/{original_db}')
            target_conn = psycopg2.connect(f'postgresql://postgres:rnrinfo@localhost:5432/{new_db_name}')
            
            source_cur = source_conn.cursor()
            target_cur = target_conn.cursor()
            
            # Copy accounts_master
            source_cur.execute("SELECT * FROM accounts_master")
            accounts = source_cur.fetchall()
            
            if accounts:
                # Get column names
                source_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'accounts_master' ORDER BY ordinal_position")
                columns = [row[0] for row in source_cur.fetchall()]
                
                placeholders = ','.join(['%s'] * len(columns))
                insert_sql = f"INSERT INTO accounts_master ({','.join(columns)}) VALUES ({placeholders})"
                
                target_cur.executemany(insert_sql, accounts)
                print(f"   ✅ Copied {len(accounts)} accounts")
            
            # Copy companies
            source_cur.execute("SELECT * FROM companies")
            companies = source_cur.fetchall()
            
            if companies:
                source_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'companies' ORDER BY ordinal_position")
                columns = [row[0] for row in source_cur.fetchall()]
                
                placeholders = ','.join(['%s'] * len(columns))
                insert_sql = f"INSERT INTO companies ({','.join(columns)}) VALUES ({placeholders})"
                
                target_cur.executemany(insert_sql, companies)
                print(f"   ✅ Copied {len(companies)} companies")
            
            # Copy users
            source_cur.execute("SELECT * FROM users")
            users = source_cur.fetchall()
            
            if users:
                source_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position")
                columns = [row[0] for row in source_cur.fetchall()]
                
                placeholders = ','.join(['%s'] * len(columns))
                insert_sql = f"INSERT INTO users ({','.join(columns)}) VALUES ({placeholders})"
                
                target_cur.executemany(insert_sql, users)
                print(f"   ✅ Copied {len(users)} users")
            
            target_conn.commit()
            
            source_cur.close()
            source_conn.close()
            target_cur.close()
            target_conn.close()
            
        except Exception as e:
            print(f"   ❌ Error copying master data: {e}")
        
        print(f"\n🎉 New database '{new_db_name}' created successfully!")
        print(f"\n📝 To use the new database:")
        print(f"   1. Update config/env.development:")
        print(f"      DATABASE_URL=postgresql://postgres:rnrinfo@localhost/{new_db_name}")
        print(f"   2. Restart your server")
        print(f"   3. Run fresh tests")
        print(f"\n🔄 To switch back to original:")
        print(f"   DATABASE_URL=postgresql://postgres:rnrinfo@localhost/{original_db}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_new_database()