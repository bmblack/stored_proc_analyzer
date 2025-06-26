#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('config/settings.env')

def test_db_connection():
    """Test the database connection"""
    try:
        # Get connection string from environment
        connection_string = os.getenv('DB_CONNECTION_STRING')
        
        if not connection_string:
            print("❌ DB_CONNECTION_STRING not found in environment variables")
            return False
            
        print(f"🔗 Testing connection with: {connection_string}")
        
        # Create engine
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION as version"))
            version = result.fetchone()
            print(f"✅ Database connection successful!")
            print(f"📊 SQL Server Version: {version[0]}")
            
            # Test if we can see stored procedures
            result = conn.execute(text("""
                SELECT COUNT(*) as proc_count 
                FROM INFORMATION_SCHEMA.ROUTINES 
                WHERE ROUTINE_TYPE = 'PROCEDURE'
            """))
            proc_count = result.fetchone()
            print(f"📋 Found {proc_count[0]} stored procedures in the database")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure SQL Server is running in Docker")
        print("2. Check if port 1433 is accessible")
        print("3. Verify username/password (sa:Accenture#1234)")
        print("4. Ensure AdventureWorks2016 database exists")
        return False

if __name__ == "__main__":
    print("🧪 Testing Database Connection...")
    print("=" * 50)
    test_db_connection()
