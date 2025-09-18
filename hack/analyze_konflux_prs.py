#!/usr/bin/env python3
"""
Script to analyze pull requests opened by app/red-hat-konflux using cursor-agent.

This script:
1. Fetches all open PRs opened by app/red-hat-konflux
2. Passes the PR list to cursor-agent for automated analysis
3. Uses non-interactive mode to avoid permission prompts
4. Outputs analysis results directly to console
"""

import subprocess
import json
import sys
import os
from typing import List, Dict, Any


def run_command(cmd: List[str], description: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command and handle errors."""
    try:
        print(f"Running: {description}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
        return result
    except subprocess.TimeoutExpired as e:
        print(f"Timeout {description}: Command took longer than {timeout} seconds")
        print("This might be due to cursor-agent waiting for user input")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error {description}: Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Command not found: {e}")
        print("Please ensure 'gh' (GitHub CLI) and 'cursor-agent' are installed and in your PATH")
        sys.exit(1)


def get_konflux_prs() -> List[Dict[str, Any]]:
    """Fetch all open PRs opened by app/red-hat-konflux."""
    repo = "openshift/sandboxed-containers-operator"
    author = "app/red-hat-konflux"
    
    cmd = [
        "gh", "pr", "list",
        "--repo", repo,
        "--author", author,
        "--state", "open",
        "--json", "number,title,url,createdAt,updatedAt,body"
    ]
    
    result = run_command(cmd, f"fetching PRs from {author}")
    prs = json.loads(result.stdout)
    
    print(f"Found {len(prs)} open PRs from {author}")
    return prs


def format_prs_for_analysis(prs: List[Dict[str, Any]]) -> str:
    """Format PR data for Cursor analysis."""
    if not prs:
        return "No open PRs found from app/red-hat-konflux."
    
    formatted_prs = []
    for pr in prs:
        formatted_pr = f"PR #{pr['number']}: {pr['title']} - {pr['url']}"
        formatted_prs.append(formatted_pr)
    
    return "\n".join(formatted_prs)


def analyze_with_cursor_agent(pr_data: str) -> None:
    """Analyze PR data using cursor-agent."""
    # Load the analysis prompt template
    template_file = "hack/analysis_prompt_template.txt"
    try:
        with open(template_file, 'r') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: Template file {template_file} not found")
        return
    
    # Replace the placeholder with actual PR data
    analysis_prompt = template.replace("{PR_DATA}", pr_data)

    # Create a temporary file with the prompt
    temp_file = "/tmp/cursor_pr_analysis.txt"
    with open(temp_file, 'w') as f:
        f.write(analysis_prompt)
    
    # Use cursor-agent with stdin input
    cmd = ["cursor-agent", "-p", "-f", "--output-format", "text"]
    
    print("Analyzing PRs with cursor-agent...")
    print("="*60)
    
    try:
        # Use longer timeout for cursor-agent analysis (10 minutes)
        with open(temp_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True, check=True, timeout=600)
        
        print("\n" + "="*80)
        print("CURSOR-AGENT ANALYSIS RESULTS:")
        print("="*80)
        print(result.stdout)
        
        if result.stderr:
            print("\nAdditional output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error running cursor-agent: {e}")
        print("Make sure cursor-agent is properly authenticated and configured.")
        print("Try running 'cursor-agent login' if you haven't already.")
        
    #finally:
        # Clean up temporary file
        #if os.path.exists(temp_file):
        #    os.remove(temp_file)


def main():
    """Main function."""
    print("Analyzing PRs from app/red-hat-konflux...")
    print("="*50)
    
    # Set environment variable to disable GitHub CLI prompts
    os.environ["GH_NO_PROMPT"] = "1"
    
    # Check if we're in the right directory
    if not os.path.exists("go.mod"):
        print("Warning: Not in the project root directory")
    
    # Fetch PRs
    prs = get_konflux_prs()
    
    if not prs:
        print("No open PRs found from app/red-hat-konflux.")
        return
    
    # Format for analysis
    formatted_prs = format_prs_for_analysis(prs)
    
    # Show what we found
    print("\nPRs to analyze:")
    print("-" * 30)
    for pr in prs:
        print(f"PR #{pr['number']}: {pr['title']}")
    
    # Analyze with cursor-agent
    analyze_with_cursor_agent(formatted_prs)


if __name__ == "__main__":
    main()