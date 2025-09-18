# Konflux PR Analysis Script

This script fetches all open pull requests opened by `app/red-hat-konflux` in the sandboxed-containers-operator project and automatically analyzes them using cursor-agent.

## Prerequisites

- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated
- Cursor Agent (`cursor-agent`) installed and authenticated
- Access to the openshift/sandboxed-containers-operator repository

## Files

- `analyze_konflux_prs.py` - Main script
- `analysis_prompt_template.txt` - Template file for the analysis prompt
- `README_analyze_konflux_prs.md` - This documentation

## Usage

```bash
# From the project root directory
python3 hack/analyze_konflux_prs.py
```

## What it does

1. **Fetches PRs**: Uses GitHub CLI to get all open PRs from `app/red-hat-konflux`
2. **Formats data**: Creates a comprehensive prompt with PR details including:
   - PR number and title
   - URL and timestamps
   - Description/body content
3. **Automated analysis**: Uses cursor-agent to analyze the PRs and provide detailed insights
4. **Console output**: Displays the complete analysis directly in the terminal

## Analysis Focus

The generated prompt asks Cursor to analyze:
- Summary of changes across all PRs
- Potential issues or concerns
- Review priorities
- Patterns and trends
- Code quality and best practices
- Security implications
- Performance impact
- Compatibility with existing code
- Testing coverage

## Example Output

The script will show:
- Number of PRs found
- List of PR titles
- Detailed analysis from cursor-agent including:
  - Summary of changes across all PRs
  - Potential issues and concerns
  - Review priorities
  - Patterns and trends
  - Specific recommendations

## Non-interactive Mode

The script automatically:
- Sets `GH_NO_PROMPT=1` to avoid GitHub CLI interactive prompts
- Uses cursor-agent with `-p` flag for non-interactive analysis
- Outputs results directly to console without requiring user interaction

## Authentication

Make sure cursor-agent is authenticated:
```bash
cursor-agent login
```

The script will work seamlessly once both GitHub CLI and cursor-agent are properly authenticated.

## Customizing the Analysis Prompt

You can modify the analysis prompt by editing `hack/analysis_prompt_template.txt`. The template uses `{PR_DATA}` as a placeholder that gets replaced with the actual PR information.

Example template modifications:
- Add specific analysis criteria
- Change the output format requirements
- Include additional context about the project
- Modify the focus areas for analysis
