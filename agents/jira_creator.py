from jira import JIRA
import os

def connect_jira():
    return JIRA(
        server=os.getenv("JIRA_SERVER"),
        basic_auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_TOKEN"))
    )

def create_ticket(jira, summary, description, project="APP"):
    issue_dict = {
        'project': {'key': project},
        'summary': summary,
        'description': description,
        'issuetype': {'name': 'Story'}
    }
    return jira.create_issue(fields=issue_dict)
