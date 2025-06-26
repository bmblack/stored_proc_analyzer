import streamlit as st
import os
from dotenv import load_dotenv
from agents.schema_crawler import extract_schema
from agents.reverse_engineer import reverse_engineer
from agents.complexity_analyzer import analyze
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

if st.button("Run Analysis"):
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

    write_csv(combined)
    write_summary(combined)
    st.session_state.analysis_complete = True
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

# Show download buttons if analysis is complete
if st.session_state.analysis_complete:
    if os.path.exists("outputs/analysis.csv"):
        with open("outputs/analysis.csv", "rb") as file:
            st.download_button(
                label="Download CSV",
                data=file.read(),
                file_name="analysis.csv",
                mime="text/csv"
            )
    
    if os.path.exists("outputs/summary.docx"):
        with open("outputs/summary.docx", "rb") as file:
            st.download_button(
                label="Download Word Summary",
                data=file.read(),
                file_name="summary.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    
    # Add a button to reset and run new analysis
    if st.button("Run New Analysis"):
        st.session_state.analysis_complete = False
        st.rerun()
