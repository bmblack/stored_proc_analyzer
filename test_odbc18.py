#!/usr/bin/env python3

import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/settings.env')

def list_available_drivers():
    """List available ODBC drivers"""
    print("🔍 Available ODBC Drivers:")
    drivers = pyodbc.drivers()
    for driver in drivers:
        print(f"   - {driver}")
    return drivers

def test_odbc_connection():
    """Test ODBC connection with different drivers and servers"""
    
    available_drivers = list_available_drivers()
    
    # Try different combinations
    servers = ['127.0.0.1,1433', 'localhost,1433', '127.0.0.1:1433', 'localhost:1433']
    drivers_to_try = []
    
    # Check which SQL Server drivers are available
    for driver in available_drivers:
        if 'SQL Server' in driver:
            drivers_to_try.append(driver)
    
    if not drivers_to_try:
        print("❌ No SQL Server ODBC drivers found!")
        return None, None
    
    print(f"\n🔧 Will test with drivers: {drivers_to_try}")
    print(f"🔧 Will test with servers: {servers}")
    
    connection_templates = [
        "DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID=sa;PWD=Accenture#1234;TrustServerCertificate=yes;Encrypt=no",
        "DRIVER={{{driver}}};SERVER={server};DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234;TrustServerCertificate=yes;Encrypt=no",
        "DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID=sa;PWD=Accenture#1234;Encrypt=no",
        "DRIVER={{{driver}}};SERVER={server};DATABASE=AdventureWorks2016;UID=sa;PWD=Accenture#1234;Encrypt=no"
    ]
    
    attempt = 1
    for driver in drivers_to_try:
        for server in servers:
            for template in connection_templates:
                conn_str = template.format(driver=driver, server=server)
                
                print(f"\n🔗 Attempt {attempt}: Testing connection...")
                print(f"Driver: {driver}")
                print(f"Server: {server}")
                print(f"Connection: {conn_str}")
                
                try:
                    # Test connection
                    conn = pyodbc.connect(conn_str, timeout=10)
                    cursor = conn.cursor()
                    
                    # Test query
                    cursor.execute("SELECT @@VERSION")
                    version = cursor.fetchone()[0]
                    print(f"✅ Connection successful!")
                    print(f"📊 SQL Server Version: {version[:100]}...")
                    
                    # Test database access
                    if 'DATABASE=master' in conn_str:
                        cursor.execute("SELECT name FROM sys.databases WHERE name = 'AdventureWorks2016'")
                        if cursor.fetchone():
                            print(f"✅ AdventureWorks2016 database confirmed!")
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM INFORMATION_SCHEMA.ROUTINES 
                            WHERE ROUTINE_TYPE = 'PROCEDURE'
                        """)
                        proc_count = cursor.fetchone()[0]
                        print(f"📋 Found {proc_count} stored procedures")
                    
                    cursor.close()
                    conn.close()
                    
                    print(f"🎉 Working connection found!")
                    
                    # Convert to SQLAlchemy format
                    import urllib.parse
                    encoded_conn = urllib.parse.quote_plus(conn_str)
                    sqlalchemy_conn = f"mssql+pyodbc:///?odbc_connect={encoded_conn}"
                    
                    return conn_str, sqlalchemy_conn
                    
                except Exception as e:
                    print(f"❌ Connection failed: {str(e)}")
                    
                attempt += 1
    
    print(f"\n❌ All connection attempts failed!")
    return None, None

if __name__ == "__main__":
    print("🧪 Testing ODBC Connection with Different Drivers...")
    print("=" * 60)
    pyodbc_conn, sqlalchemy_conn = test_odbc_connection()
    
    if pyodbc_conn:
        print(f"\n✅ SUCCESS!")
        print(f"PyODBC format: {pyodbc_conn}")
        print(f"SQLAlchemy format: {sqlalchemy_conn}")
        print(f"\n📝 Update your config/settings.env with:")
        print(f"DB_CONNECTION_STRING={sqlalchemy_conn}")
    else:
        print(f"\n❌ No working connection found.")
        print(f"\n🔧 Additional troubleshooting:")
        print(f"1. Check if Docker container is accessible from host")
        print(f"2. Try: docker port SQL_Server_Docker")
        print(f"3. Try: telnet localhost 1433")
