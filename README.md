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

### Agent Specialization & Roles

- **SummaryAgent**: 
  - **Role**: Reverse Engineer
  - **Goal**: Generate high-level business summaries of SQL stored procedures
  - **Tools**: Reverse Engineer Procedure tool (uses LLM for business logic analysis)
  - **Backstory**: Database expert who understands SQL logic and can summarize functionality

- **ComplexityAgent**: 
  - **Role**: Analyzer  
  - **Goal**: Determine complexity scores for each procedure
  - **Tools**: Analyze Complexity tool (custom logic for technical assessment)
  - **Backstory**: Assesses code complexity based on size, control structures, and database patterns

### Orchestration Architecture

Our CrewAI implementation demonstrates **true agent orchestration** through:

#### 🤖 **Agent Coordination**
```python
crew = Crew(
    agents=[summary_agent, complexity_agent],
    tasks=[summary_task, complexity_task],
    process="sequential"  # Coordinated workflow
)
```

#### 🔄 **Workflow Management**
- **Sequential Processing**: Tasks execute in coordinated order
- **Agent Autonomy**: Each agent independently decides how to use their specialized tools
- **Task Dependencies**: Later tasks can build upon earlier agent results
- **Error Handling**: Graceful fallbacks maintain workflow integrity

#### 🛠️ **Tool Integration**
- **Specialized Tools**: Each agent has domain-specific analysis capabilities
- **Context Sharing**: Global procedure context allows tools to access necessary data
- **Type Safety**: Tools use proper type hints for CrewAI parameter passing

### Orchestration vs Direct Function Calls

**Without Orchestration (Simple Approach):**
```python
summary = reverse_engineer(proc)
complexity = analyze(proc)
```

**With CrewAI Orchestration:**
```python
# Agents work together autonomously
crew = Crew(agents=[summary_agent, complexity_agent], tasks=[...])
result = crew.kickoff()  # Coordinated execution
```

### Benefits of Agent Orchestration

1. **Scalability**: Easy to add more agents or modify workflow without changing core logic
2. **Separation of Concerns**: Each agent focuses on its specialized domain
3. **Autonomous Decision Making**: Agents independently determine tool usage strategies
4. **Workflow Flexibility**: Crew manages task execution order and agent interaction
5. **Error Resilience**: Individual agent failures don't break the entire workflow

Each agent is paired with specialized `Tasks` and orchestrated via a `Crew` that runs tasks in sequence, demonstrates inter-agent coordination, and collects results from the autonomous agent workflow.

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

## 🏠 Local Development Setup

### Using AdventureWorks Sample Database

For local development and testing, we recommend using Microsoft's **AdventureWorks** sample database, which contains realistic stored procedures perfect for demonstrating this project's capabilities.

#### Why AdventureWorks?
- ✅ Contains **real-world stored procedures** of varying complexity levels
- ✅ Demonstrates all agent coordination features effectively  
- ✅ No sensitive data concerns for proof of concept development
- ✅ Well-documented and widely used in the SQL Server community

#### Quick Setup Instructions

1. **Download AdventureWorks Database**:
   - Visit: https://github.com/Microsoft/sql-server-samples/releases/tag/adventureworks
   - Download `AdventureWorks2019.bak` (recommended) or `AdventureWorks2017.bak`
   - These contain the most stored procedures for analysis

2. **Restore Database** (SQL Server Management Studio):
   ```sql
   RESTORE DATABASE AdventureWorks2019 
   FROM DISK = 'C:\path\to\AdventureWorks2019.bak'
   WITH REPLACE;
   ```

3. **Update Connection String** in `config/settings.env`:
   ```bash
   # AdventureWorks local connection example
   DB_CONNECTION_STRING=mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3Dlocalhost%2C1433%3BDATABASE%3DAdventureWorks2019%3BUID%3Dsa%3BPWD%3Dyour-password%3BTrustServerCertificate%3Dyes%3BEncrypt%3Dno
   ```

4. **Test Connection**:
   ```bash
   python test_connection.py
   ```

#### What You'll Analyze
AdventureWorks contains **~20 stored procedures** including:
- Simple procedures (complexity 1-2): Basic CRUD operations
- Medium procedures (complexity 3-5): Business logic with joins
- Complex procedures (complexity 6+): Advanced operations with cursors, loops, and error handling

This variety perfectly demonstrates how the AI agents coordinate to analyze different complexity levels and generate appropriate recommendations.

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
