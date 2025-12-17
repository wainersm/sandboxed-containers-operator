---
name: prowjob-analyze
description: Analyze OpenShift Prow job results to determine status, extract metadata, and identify failures
allowed-tools:
  - Bash(python3 scripts/prowjob-analyzer/analyze.py:*)
---

Run the Prow job analyzer script:

```bash
python3 scripts/prowjob-analyzer/analyze.py --no-wait "$@"
```

---

## About

Analyze a Prow job to extract metadata, determine pass/fail status, and provide detailed failure analysis.

**Usage:**
```
/prowjob-analyze <PROW_JOB_URL>
```

**Example:**
```
/prowjob-analyze https://prow.ci.openshift.org/view/gs/test-platform-results/logs/periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-aws-ipi-peerpods/1987995564184178688
```

**What it does:**
1. Extracts job metadata (provider, OCP version, Kata RPM, etc.)
2. Determines overall job status (pass/fail/timeout)
3. For failures, identifies WHERE (test step, prow step, infrastructure)
4. Lists failing tests with categorization
5. Analyzes logs for common failure patterns
6. Generates human-readable and machine-parsable reports
7. Provides links to relevant artifacts
8. Determines if human intervention is needed

**Output:**
- Comprehensive analysis report in markdown format
- Machine-readable JSON summary (with --json flag)
- Links to all relevant artifacts

**Options:**
- `--json`: Output machine-readable JSON format
- `--verbose`: Show detailed progress information
- `--wait`: Wait for in-progress jobs to complete (default: true, timeout: 5 minutes)
