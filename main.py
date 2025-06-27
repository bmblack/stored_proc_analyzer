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

# Core functions that can be called directly
def reverse_engineer_logic(proc):
    """Core logic for reverse engineering a stored procedure."""
    return call_llm(REVERSE_ENGINEER_PROMPT.format(name=proc["name"], code=proc["definition"]))

def complexity_analysis_logic(proc):
    """Core logic for analyzing complexity of a stored procedure."""
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

# CrewAI tool wrappers that work with the current procedure context
# Global counter to make tool calls unique
tool_call_counter = 0

@tool("Reverse Engineer Procedure")
def reverse_engineer_tool(procedure_name: str, analysis_context: str = "default") -> str:
    """Reverse engineer a stored procedure to understand its business logic and functionality.
    Args:
        procedure_name: The name of the stored procedure to analyze
        analysis_context: Context information for this analysis (used to ensure uniqueness)
    Returns:
        A business summary of what the stored procedure does
    """
    global tool_call_counter
    tool_call_counter += 1
    
    # Strip any trailing numbers or spaces that might be added by CrewAI
    clean_name = procedure_name.strip().split()[0] if procedure_name else ""
    
    # Create unique call identifier
    unique_call_id = f"{clean_name}_analysis_{analysis_context}_{tool_call_counter}"
    
    try:
        # Find the procedure in the current context
        for proc in current_procedures:
            if proc["name"] == clean_name:
                print(f"   🔍 Found procedure {clean_name}, analyzing... (Context: {analysis_context}, Call ID: {unique_call_id})")
                result = reverse_engineer_logic(proc)
                print(f"   ✅ Analysis complete for {clean_name}")
                return result
        return f"Could not find procedure {clean_name} in current context (Context: {analysis_context}, Call ID: {unique_call_id})"
    except Exception as e:
        error_msg = f"Error analyzing procedure {clean_name}: {str(e)} (Context: {analysis_context}, Call ID: {unique_call_id})"
        print(f"   ❌ {error_msg}")
        return error_msg

@tool("Analyze Complexity")
def complexity_tool(procedure_name: str, complexity_context: str = "default") -> dict:
    """Analyze the complexity of a stored procedure based on size, control structures, and database patterns.
    Args:
        procedure_name: The name of the stored procedure to analyze
        complexity_context: Context information for this complexity analysis (used to ensure uniqueness)
    Returns:
        A dictionary with complexity score, lines of code, and complexity factors
    """
    global tool_call_counter
    tool_call_counter += 1
    
    # Strip any trailing numbers or spaces that might be added by CrewAI
    clean_name = procedure_name.strip().split()[0] if procedure_name else ""
    
    unique_call_id = f"{clean_name}_complexity_{complexity_context}_{tool_call_counter}"
    
    # Find the procedure in the current context
    for proc in current_procedures:
        if proc["name"] == clean_name:
            print(f"   🔍 Analyzing complexity for {clean_name}... (Context: {complexity_context}, Call ID: {unique_call_id})")
            result = complexity_analysis_logic(proc)
            print(f"   ✅ Complexity analysis complete for {clean_name}")
            return result
    return {"complexity": 0, "lines_of_code": 0, "complexity_factors": f"Could not find procedure {clean_name} (Context: {complexity_context}, Call ID: {unique_call_id})"}

# Global variable to hold current procedures for tools
current_procedures = []

def main():
    global current_procedures
    
    print("🚀 Starting CrewAI Stored Procedure Analysis...")
    print("📊 Extracting stored procedures from database...")
    
    procs = extract_schema()
    current_procedures = procs  # Set global variable for tools to access
    print(f"✅ Found {len(procs)} stored procedures")

    summaries = []
    technical_analyses = []

    print(f"\n🤖 CrewAI agents will be created fresh for each procedure - beginning analysis...")
    
    for i, proc in enumerate(procs, 1):
        print(f"📋 Analyzing procedure {i}/{len(procs)}: {proc['name']}")
        
        # Reset tool counter for each procedure to ensure uniqueness
        global tool_call_counter
        tool_call_counter = i * 100  # Ensure unique counter per procedure
        
        # Create fresh agents for each procedure to avoid repetition detection
        summary_agent = Agent(
            name=f"SummaryAgent_{i}",
            role=f"Reverse Engineer #{i}",
            goal=f"Generate high-level summary of SQL stored procedure #{i}: {proc['name']}",
            backstory=f"You are a database expert analyzing procedure #{i} of {len(procs)}. You understand SQL logic and can summarize stored procedure functionality for {proc['name']}.",
            tools=[reverse_engineer_tool],
            verbose=True,
            allow_delegation=False
        )

        complexity_agent = Agent(
            name=f"ComplexityAgent_{i}",
            role=f"Complexity Analyzer #{i}",
            goal=f"Determine complexity score for procedure #{i}: {proc['name']}",
            backstory=f"You assess how complex SQL code is for procedure #{i} of {len(procs)}. You analyze size and features like cursors or joins in {proc['name']}.",
            tools=[complexity_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Create tasks with highly unique descriptions to prevent CrewAI anti-repetition
        import time
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        
        summary_task = Task(
            agent=summary_agent,
            description=f"Analysis Task {timestamp}-{i}: Perform reverse engineering analysis on stored procedure named '{proc['name']}'. This is procedure number {i} out of {len(procs)} total procedures. Use the Reverse Engineer Procedure tool with procedure_name='{proc['name']}' and analysis_context='business_analysis_proc_{i}_timestamp_{timestamp}' to understand the business logic, data flow, and functional purpose of this specific database procedure. Focus on what business problem this procedure solves. IMPORTANT: Always include the analysis_context parameter with the exact value specified to ensure uniqueness.",
            expected_output=f"A comprehensive business summary explaining what stored procedure '{proc['name']}' accomplishes"
        )

        complexity_task = Task(
            agent=complexity_agent,
            description=f"Complexity Assessment {timestamp}-{i}: Evaluate the technical complexity of stored procedure '{proc['name']}' which is item {i} in our analysis queue of {len(procs)} procedures. Use the Analyze Complexity tool with procedure_name='{proc['name']}' and complexity_context='technical_complexity_proc_{i}_timestamp_{timestamp}' to examine code structure, control flow patterns, database operations, and assign an appropriate complexity rating from 1-10 based on technical factors. IMPORTANT: Always include the complexity_context parameter with the exact value specified to ensure uniqueness.",
            expected_output=f"A detailed complexity analysis with numeric score for procedure '{proc['name']}'"
        )

        # Create crew with fresh agents and more flexible configuration
        crew = Crew(
            agents=[summary_agent, complexity_agent],
            tasks=[summary_task, complexity_task],
            verbose=True,
            max_iter=5,    # Increased iterations to allow for retries
            process="sequential",
            memory=False,  # Disable memory to prevent cross-procedure interference
            step_callback=lambda step: print(f"   🔄 Step completed: {step.agent_name if hasattr(step, 'agent_name') else 'Unknown'}")
        )
        
        try:
            # Execute the crew with timeout protection
            print(f"   🚀 Starting CrewAI analysis for {proc['name']}...")
            result = crew.kickoff()
            
            # Get results from the core logic functions as backup
            complexity_data = complexity_analysis_logic(proc)
            summary_text = reverse_engineer_logic(proc)
            
            # Use CrewAI results if available, otherwise use direct function results
            if hasattr(result, 'tasks_output') and len(result.tasks_output) >= 1:
                crew_summary = result.tasks_output[0].raw if result.tasks_output[0] else summary_text
                # For complexity, we'll use our direct calculation since it returns structured data
                summary_text = crew_summary
                print(f"   ✅ CrewAI analysis successful for {proc['name']}")
            else:
                print(f"   ⚠️  CrewAI returned no results, using direct analysis for {proc['name']}")
            
        except Exception as e:
            print(f"   ⚠️  CrewAI execution issue for {proc['name']}: {str(e)[:100]}... Using direct analysis.")
            # Fallback to direct function calls
            complexity_data = complexity_analysis_logic(proc)
            summary_text = reverse_engineer_logic(proc)
        
        summary = {
            "sp_name": proc["name"],
            "summary": summary_text,
            "complexity": complexity_data["complexity"],
            "lines_of_code": complexity_data["lines_of_code"],
            "complexity_factors": complexity_data["complexity_factors"],
            "last_execution_time": proc["last_execution_time"]
        }
        summaries.append(summary)
        
        print(f"   ✅ Completed - Complexity: {complexity_data['complexity']}/10")

    print(f"\n📄 Generating reports...")
    write_csv(summaries)
    high_complexity_count = write_summary(summaries, technical_analyses)
    
    print(f"\n🎉 CrewAI Analysis Complete!")
    print(f"📊 Total procedures analyzed: {len(procs)}")
    print(f"🔧 High-complexity procedures (>3): {high_complexity_count}")
    print(f"📁 Reports saved to outputs/ directory:")
    print(f"   - outputs/analysis.csv (business summaries)")
    print(f"   - outputs/summary.docx (technical refactoring analysis)")

if __name__ == "__main__":
    main()
