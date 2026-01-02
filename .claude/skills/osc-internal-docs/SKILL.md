---
name: osc-internal-docs
description: Provides access to OSC internal documentation at osc.pages.redhat.com. Use when questions involve internal team processes, testing procedures, CI/CD workflows, release processes, debugging workflows, or cluster provisioning that aren't in official user guides.
---

# OSC Internal Documentation Reader

This skill provides access to the internal OSC team documentation hosted at https://osc.pages.redhat.com/documentation/. Use this when the user's question is about internal processes, development workflows, or team-specific information that wouldn't be in the official user guides.

## When to Use This Skill

Trigger this skill for questions about:
- **Internal testing procedures** - CI/CD, Prow jobs, test infrastructure
- **Development workflows** - Building, releasing, versioning processes
- **Cluster provisioning** - Setting up test clusters (ClusterBot, kcli, kind)
- **Debugging workflows** - Internal debugging procedures and tools
- **Release processes** - Konflux configuration, release planning
- **Team processes** - Upstream vs downstream testing, QE workflows
- **Internal architecture** - How CI/CD pipelines work, test environments

## Do NOT Use This Skill For

- Official OSC user documentation (use `osc-user-guide` skill instead)
- Basic OSC concepts, installation, or usage (use official docs)
- Questions that can be answered from the codebase alone

## Documentation Structure

The internal documentation site has the following main sections:

### Base URL
https://osc.pages.redhat.com/documentation/

### Main Sections

1. **Deploying** (`/deploying/`)
   - `/deploying/ocp` - Installing OpenShift Container Platform
   - `/deploying/operators` - Operators needed for OSC
   - `/deploying/testing-basic-workloads` - Testing basic workloads
   - `/deploying/what-is-next` - Next steps after deployment

2. **Debugging** (`/debugging/`)
   - `/debugging/cloud` - Cloud-related debugging for Peerpods

3. **Testing** (`/testing/`)
   - `/testing` - Main testing page (cluster options, test categories, CI infrastructure)

4. **Releasing** (`/releasing/`)
   - `/releasing` - Release process and Konflux configuration

### Versions
The documentation has multiple versions available:
- `/next/` - Latest development version
- `/1.10.0/` - Version 1.10.0
- `/1.9.0/` - Version 1.9.0
- `/1.8.0/` - Version 1.8.0
- `/1.7.0/` - Version 1.7.0

Default (no version prefix) shows the current stable version.

## How to Use This Skill

When this skill is activated, follow these steps:

### 1. Understand the Question

Analyze what the user is asking and determine which section(s) of the internal docs are most relevant:
- Testing/CI questions → `/testing` section
- Debugging questions → `/debugging/cloud` section
- Release questions → `/releasing` section
- Setup/deployment questions → `/deploying/` section

### 2. Fetch the Relevant Documentation

Use the WebFetch tool to retrieve content from the appropriate pages:

```bash
# Example: Fetch testing documentation
WebFetch url="https://osc.pages.redhat.com/documentation/testing"
        prompt="Extract detailed information about [specific topic]"

# Example: Fetch cloud debugging docs
WebFetch url="https://osc.pages.redhat.com/documentation/debugging/cloud"
        prompt="Extract debugging procedures for [specific issue]"

# Example: Fetch release process docs
WebFetch url="https://osc.pages.redhat.com/documentation/releasing"
        prompt="Extract information about the release process and configuration"
```

### 3. Fetch Multiple Pages if Needed

You can fetch multiple related pages in parallel using multiple WebFetch calls:

```bash
# Fetch multiple sections at once
WebFetch url="https://osc.pages.redhat.com/documentation/testing"
WebFetch url="https://osc.pages.redhat.com/documentation/debugging/cloud"
```

### 4. Follow Links to Sub-pages

If the main section page references sub-pages or specific topics:
- Look for links in the fetched content
- Construct the full URL (e.g., `https://osc.pages.redhat.com/documentation/deploying/operators`)
- Fetch those pages for more detailed information

### 5. Provide Comprehensive Answers

Based on the fetched documentation:
- Answer the user's question directly
- Include relevant commands, procedures, or workflows
- Mention which section of the internal docs the info comes from
- Provide direct links to the documentation pages
- Note if the information is version-specific

## Search Strategy

### For Broad Questions
1. Start with the main section page (e.g., `/testing`)
2. Extract the structure and available sub-topics
3. Fetch specific sub-pages as needed

### For Specific Questions
1. Directly fetch the most relevant page
2. Extract the specific information needed
3. Fetch related pages if more context is needed

### For Debugging Questions
1. Fetch `/debugging/cloud` for Peerpods issues
2. Look for specific service debugging steps
3. Extract relevant commands and log locations

### For Testing/CI Questions
1. Fetch `/testing` for test infrastructure info
2. Look for Prow job information, CI configurations
3. Extract cluster provisioning procedures if needed

## Important Notes

- **Internal Documentation**: This is for OSC team members only
- **Not a Replacement**: Official user guides are still the primary source for user-facing docs
- **Version Awareness**: Note which version the user is asking about
- **Links**: Always provide direct links back to the internal docs
- **Updates**: Internal docs may change; always fetch fresh content

## Example Usage Scenarios

### Example 1: CI/Testing Question
**User asks**: "How do I provision a temporary OCP cluster for testing?"

**Actions**:
1. Fetch `https://osc.pages.redhat.com/documentation/testing`
2. Extract information about ClusterBot, kcli, kind
3. Provide commands and procedures for cluster provisioning

### Example 2: Debugging Question
**User asks**: "How do I debug PodVM startup issues?"

**Actions**:
1. Fetch `https://osc.pages.redhat.com/documentation/debugging/cloud`
2. Extract PodVM debugging section
3. Provide service startup sequence, log locations, verification commands

### Example 3: Release Process Question
**User asks**: "What's the Konflux release configuration?"

**Actions**:
1. Fetch `https://osc.pages.redhat.com/documentation/releasing`
2. Extract Konflux configuration details
3. Provide repo links and configuration file paths

## Available Tools

This skill uses the following tools:
- **WebFetch**: Primary tool for fetching internal documentation pages
- **Read**: For reading local files if needed for context
- **Grep**: For searching codebase if documentation references code
- **Glob**: For finding files mentioned in documentation

## Team Collaboration

This skill benefits the entire OSC team by:
- Making internal docs easily accessible during development
- Providing quick answers to common workflow questions
- Reducing context switching between terminal and browser
- Ensuring team members follow documented procedures

## External Links

- **Internal Docs Site**: https://osc.pages.redhat.com/documentation/
- **GitLab Repository**: https://gitlab.cee.redhat.com/osc/documentation/
