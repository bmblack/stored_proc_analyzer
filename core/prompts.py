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

TECHNICAL_ANALYSIS_PROMPT = """
You are a senior database developer conducting a technical review of stored procedures for potential refactoring. Analyze this stored procedure:

Stored Procedure: {name}
Complexity Score: {complexity}

SQL Code:
{code}

Provide a detailed technical analysis suitable for developers considering refactoring. Include:

1. **Code Structure Analysis**: Evaluate the overall structure, organization, and readability
2. **Performance Concerns**: Identify potential performance bottlenecks, inefficient queries, or resource-intensive operations
3. **Maintainability Issues**: Highlight areas that make the code difficult to maintain, debug, or extend
4. **Best Practices Violations**: Note any deviations from SQL Server best practices
5. **Refactoring Recommendations**: Suggest specific improvements, such as:
   - Breaking down complex logic into smaller procedures
   - Optimizing queries or indexes
   - Improving error handling
   - Reducing code duplication
   - Simplifying complex conditional logic

6. **Risk Assessment**: Evaluate the risk level of refactoring this procedure (Low/Medium/High) and explain why

Focus on actionable insights that would help developers prioritize and plan refactoring efforts.
"""
