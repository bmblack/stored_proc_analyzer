#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib.parse

# Load environment variables
load_dotenv('config/settings.env')

def test_db_connection():
    """Test the database connection with different connection string formats"""
    
    # Try different connection string formats
    connection_strings = [
        # Original format
        "mssql+pyodbc://sa:Accenture#1234@localhost:1433/AdventureWorks2016?driver=ODBC+Driver+17+for+SQL+Server",
        
        # With TrustServerCertificate
        "mssql+pyodbc://sa:Accenture#1234@localhost:1433/AdventureWorks2016?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes",
        
        # With URL encoded password
        f"mssql+pyodbc://sa:{urllib.parse.quote_plus('Accenture#1234')}@localhost:1433/AdventureWorks2016?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes",
        
        # With additional timeout settings
        f"mssql+pyodbc://sa:{urllib.parse.quote_plus('Accenture#1234')}@localhost:1433/AdventureWorks2016?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&timeout=30",
        
        # Master database first
        f"mssql+pyodbc://sa:{urllib.parse.quote_plus('Accenture#1234')}@localhost:1433/master?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n🔗 Attempt {i}: Testing connection...")
        print(f"Connection string: {conn_str}")
        
        try:
            # Create engine
            engine = create_engine(conn_str)
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT @@VERSION as version"))
                version = result.fetchone()
                print(f"✅ Connection successful!")
                print(f"📊 SQL Server Version: {version[0][:100]}...")
                
                # If this is master database, check for AdventureWorks2016
                if '/master?' in conn_str:
                    result = conn.execute(text("SELECT name FROM sys.databases WHERE name = 'AdventureWorks2016'"))
                    if result.fetchone():
                        print(f"✅ AdventureWorks2016 database confirmed to exist!")
                else:
                    # Test stored procedures count
                    result = conn.execute(text("""
                        SELECT COUNT(*) as proc_count 
                        FROM INFORMATION_SCHEMA.ROUTINES 
                        WHERE ROUTINE_TYPE = 'PROCEDURE'
                    """))
                    proc_count = result.fetchone()
                    print(f"📋 Found {proc_count[0]} stored procedures")
                
                print(f"🎉 Working connection string found!")
                return conn_str
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            continue
    
    print(f"\n❌ All connection attempts failed!")
    return None

if __name__ == "__main__":
    print("🧪 Testing Database Connection with Multiple Formats...")
    print("=" * 60)
    working_conn = test_db_connection()
    
    if working_conn:
        print(f"\n✅ SUCCESS! Use this connection string:")
        print(f"DB_CONNECTION_STRING={working_conn}")
    else:
        print(f"\n❌ No working connection string found.")
