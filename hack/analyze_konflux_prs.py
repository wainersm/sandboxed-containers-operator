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
import argparse
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


def analyze_with_cursor_agent(pr_data: str) -> str:
    """Analyze PR data using cursor-agent and return the analysis output."""
    # Load the analysis prompt template
    template_file = "hack/analysis_prompt_template.txt"
    try:
        with open(template_file, 'r') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: Template file {template_file} not found")
        return ""
    
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
        
        # Return the analysis output
        return result.stdout
            
    except Exception as e:
        print(f"Error running cursor-agent: {e}")
        print("Make sure cursor-agent is properly authenticated and configured.")
        print("Try running 'cursor-agent login' if you haven't already.")
        return ""
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def analyze_actions_with_cursor_agent(analysis_output: str) -> None:
    """Analyze the analysis output to determine actions using cursor-agent."""
    action_prompt = f"""You are a Senior DevSecOps Engineer. Based on the following PR analysis, determine what actions should be taken on the low-risk PRs.

**Instructions:**
- For PRs marked as LOW RISK that have the 'needs-ok-to-test' label and all checks passed, simulate sending a comment with '/ok-to-test'
- For PRs marked as LOW RISK that have the 'ok-to-test' label and all checks passed, simulate sending a comment with '/lgtm'
- Only provide simulated actions (don't actually send comments)
- Focus on the low-risk PRs from the analysis

**Analysis Output:**
{analysis_output}

**Required Output Format:**
Provide a structured response showing:
1. PRs that would receive '/ok-to-test' comments (with PR number and title)
2. PRs that would receive '/lgtm' comments (with PR number and title)
3. Summary of actions that would be taken

Remember: These are SIMULATED actions - do not actually send any comments."""

    # Create a temporary file with the action prompt
    temp_file = "/tmp/cursor_action_analysis.txt"
    with open(temp_file, 'w') as f:
        f.write(action_prompt)
    
    # Use cursor-agent with stdin input
    cmd = ["cursor-agent", "-p", "-f", "--output-format", "text"]
    
    print("\nAnalyzing actions with cursor-agent...")
    print("="*60)
    
    try:
        # Use timeout for cursor-agent analysis (5 minutes)
        with open(temp_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True, check=True, timeout=300)
        
        print("\n" + "="*80)
        print("CURSOR-AGENT ACTION ANALYSIS RESULTS:")
        print("="*80)
        print(result.stdout)
        
        if result.stderr:
            print("\nAdditional output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error running cursor-agent for action analysis: {e}")
        print("Make sure cursor-agent is properly authenticated and configured.")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze pull requests from app/red-hat-konflux')
    parser.add_argument('-a', '--actions', action='store_true', 
                       help='After analysis, determine actions to take on low-risk PRs')
    args = parser.parse_args()
    
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
    analysis_output = analyze_with_cursor_agent(formatted_prs)
    
    # If -a flag is set, analyze actions
    if args.actions and analysis_output:
        analyze_actions_with_cursor_agent(analysis_output)


if __name__ == "__main__":
    main()