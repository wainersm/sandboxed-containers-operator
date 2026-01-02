# OSC Internal Documentation Skill

This Claude Code skill provides access to the OSC team's internal documentation hosted at https://osc.pages.redhat.com/documentation/.

## What It Does

This skill enables Claude to fetch and answer questions from the internal OSC documentation, which includes:
- Internal testing procedures and CI/CD workflows
- Debugging procedures for cloud deployments
- Cluster provisioning guides
- Release processes and Konflux configuration
- Development workflows specific to the OSC team

## When It's Used

Claude automatically uses this skill when you ask questions about:
- "How do I provision a test cluster?"
- "What's the Prow job testing workflow?"
- "How do I debug PodVM issues?"
- "What's the release process for OSC?"
- "How do CI/CD pipelines work for OSC?"

## How It Works

The skill uses Claude's WebFetch tool to retrieve content from the internal documentation site and provides comprehensive answers based on that content.

**No setup required** - The skill works out of the box since it only uses web fetching.

## Documentation Structure

The internal documentation is organized into sections:
- **Deploying**: OCP installation, operator setup, basic workload testing
- **Debugging**: Cloud/PeerPods debugging procedures
- **Testing**: CI infrastructure, test categories, cluster provisioning
- **Releasing**: Konflux configuration and release workflows

## Usage Examples

Just ask Claude naturally:

```
How do I provision a temporary OCP cluster?
```

```
Show me the PodVM debugging workflow
```

```
What's the Konflux release configuration?
```

## Difference from osc-user-guide Skill

- **osc-user-guide**: Official Red Hat user documentation (PDFs) for customers
- **osc-internal-docs**: Internal team documentation for OSC developers

Claude will automatically choose the right skill based on your question.

## Team Access

This skill requires access to the internal documentation site at `osc.pages.redhat.com`, which is available to OSC team members on the Red Hat network.

## Links

- **Internal Docs**: https://osc.pages.redhat.com/documentation/
- **GitLab Repo**: https://gitlab.cee.redhat.com/osc/documentation/
