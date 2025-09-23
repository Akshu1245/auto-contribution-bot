#!/usr/bin/env python3
import os
import requests
import json
import google.generativeai as genai
from datetime import datetime

class IssueSolver:
    def __init__(self):
        self.setup_gemini()
        self.github_token = os.getenv('GH_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY')
        
    def setup_gemini(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def get_open_issues(self):
        """Fetch open issues from the repository"""
        if not self.github_token or not self.repo:
            return []
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/repos/{self.repo}/issues'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching issues: {e}")
            return []
    
    def analyze_issue(self, issue):
        """Analyze an issue and suggest solutions"""
        if not self.model:
            return None
        
        prompt = f"""
        Analyze this GitHub issue and provide a helpful solution or response:
        
        Title: {issue['title']}
        Body: {issue['body']}
        Labels: {[label['name'] for label in issue.get('labels', [])]}
        
        Provide:
        1. A brief analysis of the problem
        2. Suggested solution or approach
        3. If it's a bug, provide debugging steps
        4. If it's a feature request, provide implementation guidance
        5. Any relevant code examples if applicable
        
        Keep the response helpful and professional.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error analyzing issue: {e}")
            return None
    
    def comment_on_issue(self, issue_number, comment):
        """Post a comment on an issue"""
        if not self.github_token or not self.repo:
            return False
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/repos/{self.repo}/issues/{issue_number}/comments'
        data = {'body': comment}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error commenting on issue: {e}")
            return False
    
    def process_issues(self):
        """Process all open issues"""
        issues = self.get_open_issues()
        processed = 0
        
        for issue in issues[:5]:  # Process up to 5 issues per run
            if issue.get('pull_request'):  # Skip pull requests
                continue
            
            print(f"Processing issue #{issue['number']}: {issue['title']}")
            
            analysis = self.analyze_issue(issue)
            if analysis:
                comment = f"""## AI Analysis & Suggestions

{analysis}

---
*This analysis was generated automatically by an AI assistant. Please review and adapt the suggestions as needed.*

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
                
                if self.comment_on_issue(issue['number'], comment):
                    processed += 1
                    print(f"Added analysis comment to issue #{issue['number']}")
        
        return processed

if __name__ == "__main__":
    solver = IssueSolver()
    count = solver.process_issues()
    print(f"Processed {count} issues")
