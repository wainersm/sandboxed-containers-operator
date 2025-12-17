# Prow Job Analyzer

A tool for analyzing OpenShift Prow job results, specifically tailored for OpenShift Sandboxed Containers (OSC) testing.

## Overview

The Prow Job Analyzer provides comprehensive analysis of Prow job runs, extracting metadata, determining pass/fail status, and identifying failure locations and root causes. It's designed to help determine if human intervention is needed or if issues are transient and safe to retry.

## Features

- **Metadata Extraction**: Automatically extracts provider, OCP version, workload type, Kata RPM version, and build information
- **Status Determination**: Accurately determines if a job passed, failed, timed out, or encountered errors
- **Failure Analysis**: Identifies where failures occurred (test step, prow step, infrastructure) and categorizes failing tests
- **Pattern Recognition**: Detects common failure patterns (timeouts, OOM, network issues, etc.)
- **Root Cause Analysis**: Attempts to determine the likely cause of failures with confidence levels
- **Human Intervention Detection**: Uses heuristics to determine if automated retry is safe or if manual investigation is needed
- **Multiple Output Formats**: Generates both human-readable markdown and machine-parsable JSON reports
- **In-Progress Job Handling**: Can wait for running jobs to complete before analysis

## Usage

### Via Claude Code Slash Command

The easiest way to use the analyzer is through the Claude Code slash command:

```
/prowjob-analyze https://prow.ci.openshift.org/view/gs/test-platform-results/logs/periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-aws-ipi-peerpods/1987995564184178688
```

The analyzer supports both job URL patterns:
- **Periodic/Postsubmit**: `https://prow.ci.openshift.org/view/gs/test-platform-results/logs/{JOB_NAME}/{BUILD_ID}`
- **Presubmit/Rehearsal**: `https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/{ORG}_{REPO}/{PR}/{JOB_NAME}/{BUILD_ID}`

### Direct CLI Usage

You can also run the analyzer directly:

```bash
# Basic usage
./analyze.py <PROW_JOB_URL>

# Generate JSON output
./analyze.py --json <PROW_JOB_URL> > report.json

# Verbose mode with no wait for in-progress jobs
./analyze.py --verbose --no-wait <PROW_JOB_URL>

# Custom wait timeout (in seconds)
./analyze.py --wait 600 <PROW_JOB_URL>
```

### Options

- `--json`: Output machine-readable JSON format instead of human-readable markdown
- `--verbose, -v`: Enable verbose logging for debugging
- `--wait SECONDS`: Set timeout for waiting for in-progress jobs (default: 300 seconds)
- `--no-wait`: Don't wait for in-progress jobs (analyze immediately)

## Output

### Human-Readable Report

The default output is a comprehensive markdown report including:

- **Job Status**: Overall success/failure with emoji indicators
- **Job Overview**: Job name, build ID, duration, trigger source
- **Environment**: Provider, OCP version, workload type, Kata RPM version, build information
- **Test Results**: Total, passed, failed, and skipped test counts with categorized failure breakdown
- **Failure Analysis**: Failure location, detected patterns, root cause, and suggested actions
- **Human Intervention**: Clear indication of whether manual investigation is needed
- **Artifacts**: Direct links to all relevant artifacts (test results, logs, must-gather data)

### JSON Report

With `--json` flag, outputs a structured JSON report suitable for automation and further processing:

```json
{
  "version": "1.0",
  "timestamp": "2025-12-16T...",
  "prowjob": {...},
  "metadata": {...},
  "test_results": {...},
  "failure_analysis": {...},
  "artifacts": {...}
}
```

## Architecture

The analyzer is built with a modular architecture:

```
prowjob-analyzer/
├── analyze.py                  # Main orchestrator script
└── lib/                        # Analysis modules
    ├── fetcher.py             # Artifact fetching and URL parsing
    ├── parser.py              # prowjob.json and test-results.yaml parsing
    ├── metadata_extractor.py  # Metadata extraction
    ├── failure_analyzer.py    # Failure analysis and pattern recognition
    └── report_generator.py    # Report generation (markdown/JSON)
```

### Key Components

1. **Fetcher**: Handles URL parsing, artifact downloading with retry logic, and waiting for in-progress jobs
2. **Parser**: Parses prowjob.json and test-results.yaml, determines job status
3. **Metadata Extractor**: Extracts provider, OCP version, workload type, Kata RPM version from job data
4. **Failure Analyzer**: Identifies failure location, categorizes tests, detects patterns, determines human intervention need
5. **Report Generator**: Formats analysis results into human-readable or machine-parsable output

## Requirements

- Python 3.6+
- `pyyaml` library (for parsing test-results.yaml)

### Installing Dependencies

```bash
# Using pip
pip install pyyaml

# Or using system package manager (Fedora/RHEL)
sudo dnf install python3-pyyaml
```

## Exit Codes

- `0`: Job passed successfully
- `1`: Job failed, timed out, or was aborted
- `2`: Analysis error (cannot fetch artifacts, invalid URL, etc.)

## Examples

### Passing Job

```bash
./analyze.py https://prow.ci.openshift.org/view/gs/test-platform-results/logs/periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-aws-ipi-peerpods/1998111460479209472
```

Output:
```markdown
# Prow Job Analysis Report

## Status: ✅ SUCCESS

## Job Overview
- **Job Name**: periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-aws-ipi-peerpods
- **Provider**: AWS
- **OCP Version**: 4.19
- **Workload**: peerpods
...
```

### Failed Periodic Job

```bash
./analyze.py https://prow.ci.openshift.org/view/gs/test-platform-results/logs/periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-azure-ipi-kata/1998111457991987200
```

Output will include failure analysis with categorized failing tests, detected patterns, and human intervention recommendation.

### Presubmit/Rehearsal Job

```bash
./analyze.py https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/openshift_release/72608/rehearse-72608-periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate417-azure-ipi-coco/2001012534630420480
```

Output for rehearsal jobs includes the PR context:
```markdown
## Job Overview
- **Job Name**: rehearse-72608-periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate417-azure-ipi-coco
- **Trigger**: rehearsal
- **Provider**: Azure
- **Workload**: confidential-containers
...
```

## OSC-Specific Features

The analyzer is tailored for OSC jobs with special handling for:

- **Workload Types**: Recognizes kata, peerpods, and confidential-containers workloads
- **Kata RPM Version**: Extracts RPM version from job artifacts or identifies node-default usage
- **Test Categorization**: Groups failing tests by OSC-relevant categories (deployment, networking, resources, peerpods, etc.)
- **Common Patterns**: Detects OSC-specific failures like Kata initialization issues
- **Version Mismatches**: Identifies EXPECTED_OPERATOR_VERSION configuration issues

## Troubleshooting

### "Failed to fetch prowjob.json"

- Check that the Prow job URL is correct
- Verify the job has completed (or use --wait to wait for completion)
- Ensure you have network access to prow.ci.openshift.org

### "pyyaml not available"

Install the pyyaml library:
```bash
pip install pyyaml
```

### Job Still Running

Use the `--wait` option to wait for job completion:
```bash
./analyze.py --wait 600 <URL>  # Wait up to 10 minutes
```

## Development

### Running Tests

```bash
# Test with a known passing job
./analyze.py <passing-job-url>

# Test with a known failing job
./analyze.py <failing-job-url>

# Test JSON output
./analyze.py --json <job-url> | jq .
```

### Adding New Failure Patterns

Edit `lib/failure_analyzer.py` and add patterns to the `FAILURE_PATTERNS` dictionary:

```python
FAILURE_PATTERNS = {
    'new_pattern': [
        r'regex pattern 1',
        r'regex pattern 2',
    ],
}
```

## Contributing

When modifying the analyzer:

1. Test with both passing and failing jobs
2. Verify both human-readable and JSON output formats
3. Update this README if adding new features
4. Ensure error handling for missing artifacts

## References

- [Prow Documentation](https://docs.prow.k8s.io/)
- [OpenShift CI Documentation](https://docs.ci.openshift.org/)
- [OSC Job Definitions](https://github.com/openshift/release/tree/master/ci-operator/config/openshift/sandboxed-containers-operator)
