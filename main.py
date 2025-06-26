from crewai import Agent, Task, Crew
from crewai.tools import tool
from agents.schema_crawler import extract_schema
from core.prompts import REVERSE_ENGINEER_PROMPT
from core.llm import call_llm
from agents.documentation_writer import write_summary
from agents.csv_generator import write_csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/settings.env')

@tool("Reverse Engineer Procedure")
def reverse_engineer_tool(proc):
    return call_llm(REVERSE_ENGINEER_PROMPT.format(name=proc["name"], code=proc["definition"]))

@tool("Analyze Complexity")
def complexity_tool(proc):
    definition_upper = proc["definition"].upper()
    lines = proc["definition"].count("\n")
    
    # Calculate complexity factors
    factors = []
    weight = 1
    
    # Check for complexity factors
    if "CURSOR" in definition_upper:
        weight = 2
        factors.append("Contains CURSOR (2x multiplier)")
    elif "JOIN" in definition_upper:
        weight = 1.5
        factors.append("Contains JOIN operations (1.5x multiplier)")
    
    # Count other complexity indicators
    if "WHILE" in definition_upper or "LOOP" in definition_upper:
        factors.append("Contains loops")
    if "IF" in definition_upper or "CASE" in definition_upper:
        factors.append("Contains conditional logic")
    if "TRY" in definition_upper and "CATCH" in definition_upper:
        factors.append("Contains error handling")
    if "TRANSACTION" in definition_upper or "BEGIN TRAN" in definition_upper:
        factors.append("Contains transaction management")
    if "EXEC" in definition_upper or "EXECUTE" in definition_upper:
        factors.append("Calls other procedures/functions")
    if "CREATE" in definition_upper and ("TABLE" in definition_upper or "VIEW" in definition_upper):
        factors.append("Creates database objects")
    
    # Add line count factor
    if lines > 100:
        factors.append(f"Large procedure ({lines} lines)")
    elif lines > 50:
        factors.append(f"Medium-sized procedure ({lines} lines)")
    else:
        factors.append(f"Small procedure ({lines} lines)")
    
    # Calculate final complexity
    complexity = min(10, int((lines / 20) * weight))
    
    # Create factors explanation
    factors_explanation = "; ".join(factors) if factors else "Simple procedure with basic operations"
    
    return {
        "complexity": complexity,
        "lines_of_code": lines,
        "complexity_factors": factors_explanation
    }

def main():
    procs = extract_schema()

    summary_agent = Agent(
        name="SummaryAgent",
        role="Reverse Engineer",
        goal="Generate high-level summaries of SQL stored procedures",
        backstory="You are a database expert who understands SQL logic and can summarize stored procedure functionality.",
        tools=[reverse_engineer_tool]
    )

    complexity_agent = Agent(
        name="ComplexityAgent",
        role="Analyzer",
        goal="Determine complexity score for each procedure",
        backstory="You assess how complex SQL code is based on size and features like cursors or joins.",
        tools=[complexity_tool]
    )

    summaries = []
    complexities = []

    for proc in procs:
        summary_task = Task(
            agent=summary_agent,
            description=f"Summarize this procedure: {proc['name']}",
            expected_output="Summary of what the stored procedure does",
            input=proc
        )

        complexity_task = Task(
            agent=complexity_agent,
            description=f"Compute complexity for: {proc['name']}",
            expected_output="Complexity score from 1 to 10",
            input=proc
        )

        crew = Crew(tasks=[summary_task, complexity_task])
        result = crew.kickoff()

        complexity_data = result[1]
        summary = {
            "sp_name": proc["name"],
            "summary": result[0],
            "complexity": complexity_data["complexity"],
            "lines_of_code": complexity_data["lines_of_code"],
            "complexity_factors": complexity_data["complexity_factors"],
            "last_execution_time": proc["last_execution_time"]
        }
        summaries.append(summary)

    write_csv(summaries)
    write_summary(summaries)

if __name__ == "__main__":
    main()
