#!/usr/bin/env python3
import os
import json
import random
from datetime import datetime, timedelta
import requests
import google.generativeai as genai

class DailyContributor:
    def __init__(self):
        self.setup_gemini()
        self.github_token = os.getenv('GH_TOKEN')
        
    def setup_gemini(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def generate_content(self):
        """Generate meaningful content for daily contribution"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if self.model:
            prompt = f"""Generate a useful programming tip, code snippet, or interesting tech fact for date {today}. 
            Make it educational and practical. Include a brief explanation."""
            
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini API error: {e}")
        
        # Fallback content
        tips = [
            "Python tip: Use list comprehensions for cleaner, more readable code.",
            "Git tip: Use 'git stash' to temporarily save uncommitted changes.",
            "JavaScript tip: Use const for variables that won't be reassigned.",
            "SQL tip: Use EXPLAIN to analyze query performance.",
            "Linux tip: Use 'grep -r' to search recursively through directories."
        ]
        return random.choice(tips)
    
    def create_daily_file(self):
        """Create a daily contribution file"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        
        # Create directory if it doesn't exist
        os.makedirs('contributions/daily_logs', exist_ok=True)
        
        content = self.generate_content()
        
        file_content = f"""# Daily Contribution - {date_str}

Date: {today.strftime('%B %d, %Y')}
Day: {today.strftime('%A')}

## Content

{content}

## Statistics

- Contribution #{self.get_contribution_count() + 1}
- Generated at: {today.strftime('%H:%M:%S UTC')}

---
*This contribution was generated automatically to maintain consistent GitHub activity.*
"""
        
        filename = f'contributions/daily_logs/{date_str}.md'
        with open(filename, 'w') as f:
            f.write(file_content)
        
        self.update_contribution_stats(date_str)
        print(f"Created daily contribution: {filename}")
    
    def get_contribution_count(self):
        """Get current contribution count"""
        try:
            with open('data/contributions.json', 'r') as f:
                data = json.load(f)
                return len(data.get('contributions', []))
        except FileNotFoundError:
            return 0
    
    def update_contribution_stats(self, date_str):
        """Update contribution statistics"""
        os.makedirs('data', exist_ok=True)
        
        try:
            with open('data/contributions.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {'contributions': []}
        
        data['contributions'].append({
            'date': date_str,
            'timestamp': datetime.now().isoformat(),
            'type': 'daily_contribution'
        })
        
        with open('data/contributions.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_readme(self):
        """Update main README with latest stats"""
        count = self.get_contribution_count()
        today = datetime.now().strftime('%Y-%m-%d')
        
        readme_content = f"""# Auto-Contribution Repository

This repository maintains daily GitHub contributions automatically.

## Statistics

- Total Contributions: {count}
- Last Updated: {today}
- Current Streak: Active

## Recent Activity

Check the [daily logs](./contributions/daily_logs/) for detailed contribution history.

## Features

- 🔄 Daily automated contributions
- 🤖 AI-powered content generation
- 📊 Contribution tracking
- 🐛 Automatic issue solving
- 📈 GitHub profile optimization

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
        
        with open('README.md', 'w') as f:
            f.write(readme_content)

if __name__ == "__main__":
    contributor = DailyContributor()
    contributor.create_daily_file()
    contributor.update_readme()
    print("Daily contribution completed!")
