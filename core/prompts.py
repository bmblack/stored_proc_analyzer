REVERSE_ENGINEER_PROMPT = """
You are a business analyst explaining database procedures to functional users. Analyze this stored procedure:

Stored Procedure: {name}

SQL Code:
{code}

Provide a concise 3-sentence summary suitable for a moderately technical functional person. Focus on:
1. What business function this procedure serves
2. What data it works with or produces
3. Any key business rules or logic it implements

Keep it clear and business-focused, avoiding technical SQL details.
"""
