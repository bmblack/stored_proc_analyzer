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

## 🖥️ Streamlit App

Run the UI with:
```bash
streamlit run streamlit_app.py
```

Features:
- One-click stored procedure analysis
- CSV + Word export downloads
- Visual feedback during processing

## 🔧 Configuration

Set the following in `config/settings.env`:
```
OPENAI_API_KEY=your-api-key
JIRA_SERVER=https://yourcompany.atlassian.net
JIRA_USER=your.email@example.com
JIRA_TOKEN=your-jira-api-token
DB_CONNECTION_STRING=your_sqlalchemy_connection_string
```

## 🏁 To Run from CLI

```bash
pip install -r requirements.txt
python main.py
```

## 📂 Output Files

- `outputs/analysis.csv`: Summary table with complexity scores
- `outputs/summary.docx`: Natural language explanation of each procedure

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
