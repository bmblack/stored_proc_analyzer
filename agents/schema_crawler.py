def extract_schema():
    from core.db_connector import get_engine
    from sqlalchemy import text
    engine = get_engine()
    query = text("""
    SELECT 
        r.ROUTINE_NAME,
        r.ROUTINE_DEFINITION,
        CASE 
            WHEN ps.last_execution_time IS NULL THEN 'Never executed'
            ELSE CONVERT(VARCHAR(19), ps.last_execution_time, 120)
        END as last_execution_time
    FROM INFORMATION_SCHEMA.ROUTINES r
    LEFT JOIN sys.dm_exec_procedure_stats ps ON 
        ps.object_id = OBJECT_ID(r.ROUTINE_SCHEMA + '.' + r.ROUTINE_NAME)
    WHERE r.ROUTINE_TYPE='PROCEDURE'
    ORDER BY r.ROUTINE_NAME;
    """)
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    return [{"name": row[0], "definition": row[1], "last_execution_time": str(row[2])} for row in results]
