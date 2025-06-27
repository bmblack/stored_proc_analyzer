import streamlit as st
import os
from dotenv import load_dotenv
from agents.schema_crawler import extract_schema
from agents.reverse_engineer import reverse_engineer
from agents.complexity_analyzer import analyze
from agents.technical_analyzer import analyze_for_refactoring
from agents.documentation_writer import write_summary
from agents.csv_generator import write_csv

# Load environment variables
load_dotenv('config/settings.env')

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

# Show Run Analysis button only when not in progress and not complete
if not st.session_state.analysis_in_progress and not st.session_state.analysis_complete:
    if st.button("Run Analysis"):
        st.session_state.analysis_in_progress = True
        st.rerun()

# Run analysis if triggered
if st.session_state.analysis_in_progress and not st.session_state.analysis_complete:
    with st.spinner("Extracting stored procedures..."):
        procs = extract_schema()
    
    # Store procedures in session state and display count
    st.session_state.procedures_list = procs
    st.session_state.current_analysis_index = 0
    st.session_state.analysis_complete = False
    
    # Display total count
    st.markdown(f"## {len(procs)} stored procedures found")
    
    # Create placeholder for the procedure list
    procedure_list_placeholder = st.empty()
    
    summaries = []
    complexities = []
    combined = []
    technical_analyses = []

    for i, proc in enumerate(procs):
        # Update current analysis index
        st.session_state.current_analysis_index = i
        
        # Update the procedure list display
        with procedure_list_placeholder.container():
            st.markdown("### Analysis Progress:")
            for j, p in enumerate(procs):
                if j < i:
                    # Already analyzed
                    st.markdown(f"✅ {j+1}. **{p['name']}** - *Completed*")
                elif j == i:
                    # Currently analyzing
                    st.markdown(f"🔄 {j+1}. **{p['name']}** - *Currently analyzing...*")
                else:
                    # Not yet analyzed
                    st.markdown(f"⏳ {j+1}. **{p['name']}** - *Pending*")
        
        # Perform the analysis
        summary = reverse_engineer(proc)
        complexity = analyze(proc)
        
        # Perform technical analysis for high-complexity procedures
        if complexity["complexity"] > 3:
            technical_analysis = analyze_for_refactoring(proc, complexity["complexity"])
            technical_analyses.append(technical_analysis)
        
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

    # Final update - mark all as complete
    with procedure_list_placeholder.container():
        st.markdown("### Analysis Progress:")
        for j, p in enumerate(procs):
            st.markdown(f"✅ {j+1}. **{p['name']}** - *Completed*")

    # Generate outputs
    write_csv(combined)
    high_complexity_count = write_summary(combined, technical_analyses)
    
    # Store results in session state
    st.session_state.analysis_complete = True
    st.session_state.analysis_in_progress = False
    st.session_state.high_complexity_count = high_complexity_count
    
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
    # Display completed procedures list
    if st.session_state.procedures_list:
        st.markdown(f"## {len(st.session_state.procedures_list)} stored procedures analyzed")
        st.markdown("### Analysis Results:")
        for i, proc in enumerate(st.session_state.procedures_list):
            st.markdown(f"✅ {i+1}. **{proc['name']}** - *Completed*")
        
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
