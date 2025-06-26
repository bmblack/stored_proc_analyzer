#!/usr/bin/env python3

import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/settings.env')

def test_direct_pyodbc():
    """Test direct pyodbc connection"""
    
    # Different connection string formats for pyodbc
    connection_strings = [
        # Standard format
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234",
        
        # With TrustServerCertificate
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234;TrustServerCertificate=yes",
        
        # With Encrypt=no
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234;Encrypt=no",
        
        # With both TrustServerCertificate and Encrypt
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234;TrustServerCertificate=yes;Encrypt=no",
        
        # Master database
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=master;UID=sa;PWD=Accenture#1234;TrustServerCertificate=yes;Encrypt=no",
        
        # With timeout
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234;TrustServerCertificate=yes;Encrypt=no;Connection Timeout=30"
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n🔗 Attempt {i}: Testing direct pyodbc connection...")
        print(f"Connection string: {conn_str}")
        
        try:
            # Test direct pyodbc connection
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Test query
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✅ Direct pyodbc connection successful!")
            print(f"📊 SQL Server Version: {version[:100]}...")
            
            # Test stored procedures if not master
            if 'DATABASE=master' not in conn_str:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.ROUTINES 
                    WHERE ROUTINE_TYPE = 'PROCEDURE'
                """)
                proc_count = cursor.fetchone()[0]
                print(f"📋 Found {proc_count} stored procedures")
            else:
                cursor.execute("SELECT name FROM sys.databases WHERE name = 'AdventureWorks2016'")
                if cursor.fetchone():
                    print(f"✅ AdventureWorks2016 database confirmed!")
            
            cursor.close()
            conn.close()
            
            print(f"🎉 Working connection string found!")
            
            # Convert to SQLAlchemy format
            sqlalchemy_conn = f"mssql+pyodbc:///?odbc_connect={conn_str.replace(';', '%3B').replace('=', '%3D').replace('{', '%7B').replace('}', '%7D').replace(' ', '%20')}"
            print(f"📝 SQLAlchemy format: {sqlalchemy_conn}")
            
            return conn_str, sqlalchemy_conn
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            continue
    
    print(f"\n❌ All direct pyodbc connection attempts failed!")
    return None, None

if __name__ == "__main__":
    print("🧪 Testing Direct PyODBC Connection...")
    print("=" * 50)
    pyodbc_conn, sqlalchemy_conn = test_direct_pyodbc()
    
    if pyodbc_conn:
        print(f"\n✅ SUCCESS!")
        print(f"PyODBC format: {pyodbc_conn}")
        print(f"SQLAlchemy format: {sqlalchemy_conn}")
    else:
        print(f"\n❌ No working connection found.")
