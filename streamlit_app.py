import streamlit as st
import os
from dotenv import load_dotenv
from urllib.parse import unquote
from agents.schema_crawler import extract_schema
from agents.reverse_engineer import reverse_engineer
from agents.complexity_analyzer import analyze
from agents.technical_analyzer import analyze_for_refactoring
from agents.documentation_writer import write_summary
from agents.csv_generator import write_csv

# Load environment variables
load_dotenv('config/settings.env')

def get_database_name():
    """Extract database name from connection string"""
    connection_string = os.getenv("DB_CONNECTION_STRING", "")
    try:
        # Decode URL-encoded connection string
        decoded = unquote(connection_string)
        # Look for DATABASE= parameter
        if "DATABASE=" in decoded:
            db_part = decoded.split("DATABASE=")[1]
            db_name = db_part.split(";")[0]
            return db_name
    except:
        pass
    return "Unknown Database"

st.title("Stored Procedure Analyzer")

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'procedures_list' not in st.session_state:
    st.session_state.procedures_list = []
if 'current_analysis_index' not in st.session_state:
    st.session_state.current_analysis_index = -1
if 'analysis_in_progress' not in st.session_state:
    st.session_state.analysis_in_progress = False
if 'high_complexity_count' not in st.session_state:
    st.session_state.high_complexity_count = 0
if 'user_stories_generated' not in st.session_state:
    st.session_state.user_stories_generated = False
if 'combined_data' not in st.session_state:
    st.session_state.combined_data = []
if 'technical_analyses' not in st.session_state:
    st.session_state.technical_analyses = []
if 'agent_progress' not in st.session_state:
    st.session_state.agent_progress = {}

# Show Run Analysis button only when not in progress and not complete
if not st.session_state.analysis_in_progress and not st.session_state.analysis_complete:
    if st.button("Run Analysis"):
        st.session_state.analysis_in_progress = True
        st.rerun()

# Run analysis if triggered
if st.session_state.analysis_in_progress and not st.session_state.analysis_complete:
    with st.spinner("🔍 Schema Crawler Agent: Connecting to database and extracting stored procedures..."):
        procs = extract_schema()
    
    # Store procedures in session state and display count
    st.session_state.procedures_list = procs
    st.session_state.current_analysis_index = 0
    st.session_state.analysis_complete = False
    
    # Display total count with database name
    db_name = get_database_name()
    st.markdown(f"## {len(procs)} stored procedures analyzed from **{db_name}** database")
    
    # Create placeholder for the procedure list
    procedure_list_placeholder = st.empty()
    
    summaries = []
    complexities = []
    combined = []
    technical_analyses = []

    # Helper function to update progress display
    def update_progress_display():
        with procedure_list_placeholder.container():
            st.markdown("### Analysis Progress:")
            for j, p in enumerate(procs):
                if j < st.session_state.current_analysis_index:
                    # Already analyzed - show completed with agent history
                    st.markdown(f"✅ {j+1}. **{p['name']}** - *Completed*")
                    if p["name"] in st.session_state.agent_progress:
                        progress = st.session_state.agent_progress[p["name"]]
                        agent_list = "<ul style='margin-left: 25px;'>"
                        agent_list += "<li><strong>Reverse Engineer Agent</strong>: <em style='color: green;'>Business logic analysis completed</em></li>"
                        agent_list += "<li><strong>Complexity Analyzer Agent</strong>: <em style='color: green;'>Complexity metrics calculated</em></li>"
                        if progress["technical_analyzer"] == "completed":
                            agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em style='color: red;'>Refactoring recommendations generated</em></li>"
                        elif progress["technical_analyzer"] == "skipped":
                            agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em style='color: orange;'>Skipped (low complexity)</em></li>"
                        agent_list += "</ul>"
                        st.markdown(agent_list, unsafe_allow_html=True)
                elif j == st.session_state.current_analysis_index:
                    # Currently analyzing - show current progress
                    st.markdown(f"🔄 {j+1}. **{p['name']}** - *Analysis in progress...*")
                    if p["name"] in st.session_state.agent_progress:
                        progress = st.session_state.agent_progress[p["name"]]
                        agent_list = "<ul style='margin-left: 25px;'>"
                        
                        # Show reverse engineer status
                        if progress["reverse_engineer"] == "active":
                            agent_list += "<li><strong>Reverse Engineer Agent</strong>: <em>Analyzing business logic...</em></li>"
                        elif progress["reverse_engineer"] == "completed":
                            agent_list += "<li><strong>Reverse Engineer Agent</strong>: <em style='color: green;'>Business logic analysis completed</em></li>"
                        
                        # Show complexity analyzer status
                        if progress["complexity_analyzer"] == "active":
                            agent_list += "<li><strong>Complexity Analyzer Agent</strong>: <em>Calculating complexity metrics...</em></li>"
                        elif progress["complexity_analyzer"] == "completed":
                            agent_list += "<li><strong>Complexity Analyzer Agent</strong>: <em style='color: green;'>Complexity metrics calculated</em></li>"
                        elif progress["complexity_analyzer"] == "pending" and progress["reverse_engineer"] == "completed":
                            agent_list += "<li><strong>Complexity Analyzer Agent</strong>: <em>Pending...</em></li>"
                        
                        # Show technical analyzer status
                        if progress["technical_analyzer"] == "active":
                            agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em>Generating refactoring recommendations...</em></li>"
                        elif progress["technical_analyzer"] == "completed":
                            agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em style='color: red;'>Refactoring recommendations generated</em></li>"
                        elif progress["technical_analyzer"] == "skipped":
                            agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em style='color: orange;'>Skipped (low complexity)</em></li>"
                        
                        agent_list += "</ul>"
                        st.markdown(agent_list, unsafe_allow_html=True)
                else:
                    # Not yet analyzed
                    st.markdown(f"⏳ {j+1}. **{p['name']}** - *Pending*")

    for i, proc in enumerate(procs):
        # Update current analysis index
        st.session_state.current_analysis_index = i
        
        # Initialize agent progress for this procedure
        if proc["name"] not in st.session_state.agent_progress:
            st.session_state.agent_progress[proc["name"]] = {
                "reverse_engineer": "pending",
                "complexity_analyzer": "pending", 
                "technical_analyzer": "pending"
            }
        
        # Agent 1: Reverse Engineer Agent
        st.session_state.agent_progress[proc["name"]]["reverse_engineer"] = "active"
        update_progress_display()
        summary = reverse_engineer(proc)
        st.session_state.agent_progress[proc["name"]]["reverse_engineer"] = "completed"
        
        # Agent 2: Complexity Analyzer Agent
        st.session_state.agent_progress[proc["name"]]["complexity_analyzer"] = "active"
        update_progress_display()
        complexity = analyze(proc)
        st.session_state.agent_progress[proc["name"]]["complexity_analyzer"] = "completed"
        
        # Agent 3: Technical Analyzer Agent (conditional)
        if complexity["complexity"] > 3:
            st.session_state.agent_progress[proc["name"]]["technical_analyzer"] = "active"
            update_progress_display()
            technical_analysis = analyze_for_refactoring(proc, complexity["complexity"])
            technical_analyses.append(technical_analysis)
            st.session_state.agent_progress[proc["name"]]["technical_analyzer"] = "completed"
        else:
            st.session_state.agent_progress[proc["name"]]["technical_analyzer"] = "skipped"
        
        # Combine all data including last execution time
        combined_data = {
            "sp_name": proc["name"],
            "summary": summary["summary"],
            "complexity": complexity["complexity"],
            "lines_of_code": complexity["lines_of_code"],
            "complexity_factors": complexity["complexity_factors"],
            "last_execution_time": proc["last_execution_time"]
        }
        combined.append(combined_data)
        summaries.append(summary)
        complexities.append(complexity)

    # Clear the progress display when analysis is complete
    procedure_list_placeholder.empty()

    # Show final report generation phase
    report_status = st.empty()
    
    # Generate CSV output
    with report_status.container():
        st.markdown("#### 📋 Final Report Generation")
        st.markdown("📋 **CSV Generator Agent**: Creating analysis spreadsheet...")
    write_csv(combined)
    
    # Generate Word document summary
    with report_status.container():
        st.markdown("#### 📋 Final Report Generation")
        st.markdown("📝 **Documentation Writer Agent**: Compiling refactoring report...")
    high_complexity_count = write_summary(combined, technical_analyses)
    
    # Clear report status
    report_status.empty()
    
    # Store results in session state
    st.session_state.analysis_complete = True
    st.session_state.analysis_in_progress = False
    st.session_state.high_complexity_count = high_complexity_count
    st.session_state.combined_data = combined
    st.session_state.technical_analyses = technical_analyses
    
    # Show completion message with summary
    st.success("Analysis complete!")

# Display procedure list if analysis has been run but not yet complete
elif st.session_state.procedures_list and not st.session_state.analysis_complete:
    st.markdown(f"## {len(st.session_state.procedures_list)} stored procedures found")
    st.markdown("### Analysis Progress:")
    for i, proc in enumerate(st.session_state.procedures_list):
        if i < st.session_state.current_analysis_index:
            st.markdown(f"✅ {i+1}. **{proc['name']}** - *Completed*")
        elif i == st.session_state.current_analysis_index:
            st.markdown(f"🔄 {i+1}. **{proc['name']}** - *Currently analyzing...*")
        else:
            st.markdown(f"⏳ {i+1}. **{proc['name']}** - *Pending*")

# Show completed analysis results and download buttons if analysis is complete
if st.session_state.analysis_complete:
    # Display completed procedures list with agent audit trail
    if st.session_state.procedures_list:
        db_name = get_database_name()
        st.markdown(f"## {len(st.session_state.procedures_list)} stored procedures analyzed from **{db_name}** database")
        st.markdown("### Analysis Results:")
        for i, proc in enumerate(st.session_state.procedures_list):
            st.markdown(f"✅ {i+1}. **{proc['name']}** - *Completed*")
            # Show agent audit trail
            if proc["name"] in st.session_state.agent_progress:
                progress = st.session_state.agent_progress[proc["name"]]
                agent_list = "<ul style='margin-left: 25px;'>"
                agent_list += "<li><strong>Reverse Engineer Agent</strong>: <em style='color: green;'>Business logic analysis completed</em></li>"
                agent_list += "<li><strong>Complexity Analyzer Agent</strong>: <em style='color: green;'>Complexity metrics calculated</em></li>"
                if progress["technical_analyzer"] == "completed":
                    agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em style='color: red;'>Refactoring recommendations generated</em></li>"
                elif progress["technical_analyzer"] == "skipped":
                    agent_list += "<li><strong>Technical Analyzer Agent</strong>: <em style='color: orange;'>Skipped (low complexity)</em></li>"
                agent_list += "</ul>"
                st.markdown(agent_list, unsafe_allow_html=True)
        
        # Show summary
        st.info(f"📊 **Summary**: {len(st.session_state.procedures_list)} procedures analyzed, {st.session_state.high_complexity_count} flagged for refactoring review (complexity > 3)")
    st.markdown("### 📥 Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if os.path.exists("outputs/analysis.csv"):
            with open("outputs/analysis.csv", "rb") as file:
                st.download_button(
                    label="📊 Download Excel/CSV Report",
                    data=file.read(),
                    file_name="stored_procedures_analysis.csv",
                    mime="text/csv",
                    help="Complete analysis with 3-sentence business summaries for all procedures"
                )
    
    with col2:
        if os.path.exists("outputs/summary.docx"):
            with open("outputs/summary.docx", "rb") as file:
                st.download_button(
                    label="📋 Download Refactoring Report",
                    data=file.read(),
                    file_name="refactoring_candidates.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    help="Detailed technical analysis for procedures with complexity > 3"
                )
    
    # JIRA User Stories Section
    st.markdown("---")
    st.markdown("### 🎫 JIRA User Stories")
    
    # Get high-complexity procedures for user story generation
    high_complexity_procs = [proc for proc in st.session_state.procedures_list if any(
        combined_data["sp_name"] == proc["name"] and combined_data["complexity"] > 3 
        for combined_data in st.session_state.get('combined_data', [])
    )]
    
    if st.session_state.high_complexity_count > 0:
        st.info(f"📋 {st.session_state.high_complexity_count} stored procedures were identified as needing refactoring. Would you like to generate JIRA user stories for these procedures?")
        
        if st.button("🎫 Generate User Stories"):
            st.session_state.user_stories_generated = True
            st.rerun()
    else:
        st.success("🎉 No stored procedures require refactoring at this time!")

# Display user stories if generated
if st.session_state.get('user_stories_generated', False) and st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown("### ✏️ Edit User Stories")
    st.info("Review and edit the user stories below before pushing to JIRA. Each story is pre-populated with information from the technical analysis.")
    
    # Get high-complexity procedures and their technical analyses
    high_complexity_data = [data for data in st.session_state.combined_data if data["complexity"] > 3]
    
    user_stories = []
    
    for i, proc_data in enumerate(high_complexity_data):
        # Find corresponding technical analysis
        tech_analysis = next((ta for ta in st.session_state.technical_analyses if ta["name"] == proc_data["sp_name"]), None)
        
        st.markdown(f"#### User Story {i+1}")
        
        # Editable title
        title = st.text_input(
            f"Title {i+1}:",
            value=f"SP Refactor - {proc_data['sp_name']}",
            key=f"title_{i}"
        )
        
        # Create description with business summary and technical analysis
        description_content = f"""**Business Function:**
{proc_data['summary']}

**Technical Analysis & Refactoring Recommendations:**
{tech_analysis['technical_analysis'] if tech_analysis else 'Technical analysis not available'}

**Complexity Factors:**
- Lines of Code: {proc_data['lines_of_code']}
- Contributing Factors: {proc_data['complexity_factors']}

**Acceptance Criteria:**

**Given** the current stored procedure has complexity issues
**When** the refactoring is completed
**Then** the procedure should have improved maintainability and reduced complexity score

**Given** the refactored stored procedure is deployed
**When** it is executed with the same inputs as the original
**Then** it should produce identical results with improved performance"""
        
        # Editable description
        description = st.text_area(
            f"Description {i+1}:",
            value=description_content,
            height=300,
            key=f"description_{i}"
        )
        
        user_stories.append({
            "title": title,
            "description": description,
            "procedure_name": proc_data['sp_name']
        })
        
        st.markdown("---")
    
    # Store user stories in session state
    st.session_state.user_stories = user_stories
    
    # Push to JIRA button (placeholder)
    if st.button("🚀 Push User Stories to JIRA", type="primary"):
        st.warning("🚧 JIRA integration coming soon! Your user stories are ready to be pushed.")
        st.success(f"✅ {len(user_stories)} user stories prepared for JIRA")
