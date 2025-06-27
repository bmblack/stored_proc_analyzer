# Stored Procedure Analyzer (with CrewAI and Streamlit)

## Overview

This project uses a team of AI agents (powered by CrewAI and OpenAI) to analyze stored procedures in your SQL database. The analysis includes:
- Reverse engineering functionality
- Complexity scoring
- Business logic extraction
- Output as CSV and Word document
- Optional JIRA story creation

## 🧠 AI Agents (CrewAI)

This project uses [CrewAI](https://github.com/joaomdmoura/crewAI) to coordinate a team of autonomous agents. Each agent is assigned a specific goal and uses tools to complete tasks based on the input stored procedures.

- **SummaryAgent**: Uses an LLM tool to reverse engineer and summarize the logic of each stored procedure.
- **ComplexityAgent**: Uses a custom logic tool to score stored procedures based on size, control structures, and database patterns (e.g., cursors, joins).
- Each agent is paired with a `Task` and orchestrated via a `Crew` that runs tasks in sequence and collects results.

## 🚀 How to Run the Application

### Option 1: Streamlit Web Interface (Recommended)

The easiest way to use the analyzer is through the web interface:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

**Streamlit Features:**
- 🎯 One-click stored procedure analysis
- 📊 Real-time progress tracking during analysis
- 📥 CSV + Word document downloads
- 🎫 JIRA user story generation for high-complexity procedures
- ✏️ Editable user stories with acceptance criteria
- 🚀 Push user stories to JIRA (integration ready)

### Option 2: Command Line Interface

For automated workflows or scripting:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI version
python main.py
```

**CLI Features:**
- Batch processing of all stored procedures
- Generates reports in `outputs/` directory
- Suitable for CI/CD pipelines or scheduled analysis

## 🔧 Configuration

1. Copy the sample configuration file:
   ```bash
   cp config/settings.env.sample config/settings.env
   ```

2. Edit `config/settings.env` with your actual values:
   ```bash
   # Required: OpenAI API key for LLM analysis
   OPENAI_API_KEY=sk-proj-your-openai-api-key-here
   
   # Required: SQL Server database connection
   DB_CONNECTION_STRING=mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3Dlocalhost%2C1433%3BDATABASE%3DYourDatabase%3BUID%3Dyour-username%3BPWD%3Dyour-password%3BTrustServerCertificate%3Dyes%3BEncrypt%3Dno
   
   # Optional: JIRA integration for ticket creation
   JIRA_SERVER=https://yourcompany.atlassian.net
   JIRA_USER=your.email@example.com
   JIRA_TOKEN=your-jira-api-token
   ```

### Database Connection Examples:
- **Local SQL Server**: `mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3Dlocalhost%2C1433%3BDATABASE%3DYourDatabase%3BUID%3Dyour-username%3BPWD%3Dyour-password%3BTrustServerCertificate%3Dyes%3BEncrypt%3Dno`
- **Azure SQL Database**: `mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3Dyour-server.database.windows.net%2C1433%3BDATABASE%3Dyour-database%3BUID%3Dyour-username%3BPWD%3Dyour-password%3BEncrypt%3Dyes%3BTrustServerCertificate%3Dno`
- **Windows Authentication**: `mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3Dyour-server%3BDATABASE%3Dyour-database%3BTrusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes`

## 📂 Output Files

The analyzer generates two distinct reports:

### 📊 Excel/CSV Report (`outputs/analysis.csv`)
- **Purpose**: Business-focused overview for all stored procedures
- **Content**: 3-sentence business summaries suitable for functional users
- **Includes**: Procedure name, business summary, complexity score, lines of code, complexity factors, last execution time

### 📋 Word Document Report (`outputs/summary.docx`)
- **Purpose**: Technical refactoring analysis for high-complexity procedures only
- **Content**: Detailed technical analysis for procedures with complexity > 3
- **Includes**: 
  - Business function summary
  - Comprehensive technical analysis with refactoring recommendations
  - Code structure evaluation
  - Performance concerns identification
  - Maintainability issues assessment
  - Best practices violations
  - Risk assessment for refactoring efforts

## 🧩 Technologies Used

- Python 3.x
- OpenAI (LLM for summarization)
- **CrewAI** (LLM-based agent orchestration)
- Streamlit (UI interface)
- SQLAlchemy (database access)
- pandas (CSV generation)
- python-docx (Word report generation)
- dotenv (config management)
- JIRA (optional: for ticket generation)
