#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('config/settings.env')

def test_db_connection():
    """Test the database connection"""
    try:
        # Get base connection string and modify to connect to master
        base_connection = os.getenv('DB_CONNECTION_STRING')
        
        if not base_connection:
            print("❌ DB_CONNECTION_STRING not found in environment variables")
            return False
        
        # Connect to master database first
        master_connection = base_connection.replace('/AdventureWorks2016', '/master')
        print(f"🔗 Testing connection to master database...")
        print(f"Connection: {master_connection}")
        
        # Create engine for master
        engine = create_engine(master_connection)
        
        # Test connection to master
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION as version"))
            version = result.fetchone()
            print(f"✅ Master database connection successful!")
            print(f"📊 SQL Server Version: {version[0]}")
            
            # Check if AdventureWorks2016 database exists
            result = conn.execute(text("""
                SELECT name FROM sys.databases 
                WHERE name = 'AdventureWorks2016'
            """))
            db_exists = result.fetchone()
            
            if db_exists:
                print(f"✅ AdventureWorks2016 database exists!")
                
                # Now test connection to AdventureWorks2016
                print(f"\n🔗 Testing connection to AdventureWorks2016...")
                aw_engine = create_engine(base_connection)
                
                with aw_engine.connect() as aw_conn:
                    # Test if we can see stored procedures in AdventureWorks2016
                    result = aw_conn.execute(text("""
                        SELECT COUNT(*) as proc_count 
                        FROM INFORMATION_SCHEMA.ROUTINES 
                        WHERE ROUTINE_TYPE = 'PROCEDURE'
                    """))
                    proc_count = result.fetchone()
                    print(f"✅ AdventureWorks2016 connection successful!")
                    print(f"📋 Found {proc_count[0]} stored procedures in AdventureWorks2016")
                    
            else:
                print(f"❌ AdventureWorks2016 database does not exist!")
                print(f"📋 Available databases:")
                result = conn.execute(text("SELECT name FROM sys.databases ORDER BY name"))
                for row in result:
                    print(f"   - {row[0]}")
                    
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure SQL Server is running in Docker")
        print("2. Check if port 1433 is accessible")
        print("3. Verify username/password (sa:Accenture#1234)")
        print("4. Try connecting to master database first")
        return False

if __name__ == "__main__":
    print("🧪 Testing Database Connection...")
    print("=" * 50)
    test_db_connection()
