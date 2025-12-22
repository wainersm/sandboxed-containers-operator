---
name: prowjob-analyze
description: Analyze OpenShift Prow job results to determine status, extract metadata, and identify failures
allowed-tools:
  - Bash(python3 scripts/prowjob-analyzer/analyze.py:*)
  - Bash(python3 scripts/prowjob-analyzer/test_report.py:*)
---

Analyze a Prow job to determine its status and provide detailed failure analysis.

**Workflow:**
1. Run the main analyzer to get overall job status and metadata
2. If the job failed during the test step with test failures, automatically run detailed test analysis on failing tests

Execute the following steps:

**Step 1: Run main analyzer**
```bash
python3 scripts/prowjob-analyzer/analyze.py --no-wait "$@"
```

**Step 2: Analyze the output**
- Review the analysis report from Step 1
- Check the "Failure Location" section
- Look for "Failed Tests" listed by category

**Step 3: If test failures detected**
If the report shows:
- Failure Location: `test_step`
- Failed Tests are listed

Then run detailed test analysis:
```bash
python3 scripts/prowjob-analyzer/test_report.py <PROW_JOB_URL> <TEST_NAME_1> <TEST_NAME_2> ...
```

Use the exact test names from the "Failed Tests" section of the analyzer report.

---

## About

Comprehensive Prow job analysis with two-level investigation:

**Level 1: Overall Analysis** (analyze.py)
- Extracts job metadata (provider, OCP version, Kata RPM, catalog, etc.)
- Determines overall job status (pass/fail/timeout)
- Identifies failure location (test step, prow step, infrastructure)
- Lists failing tests with categorization
- Detects common failure patterns
- Determines if human intervention is needed

**Level 2: Detailed Test Debugging** (test_report.py - automatic for test failures)
- Extracts error messages from build logs
- Provides log context around each failure
- Detects test-specific patterns (timeout, OOM, network, etc.)
- Offers debugging hints based on detected patterns

**Usage:**
```
/prowjob-analyze <PROW_JOB_URL>
```

**Example:**
```
/prowjob-analyze https://prow.ci.openshift.org/view/gs/test-platform-results/logs/periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-aws-ipi-peerpods/1987995564184178688
```

**Output:**
- Comprehensive analysis report in markdown format
- For test failures: Detailed debugging information for each failing test
- Links to all relevant artifacts
- Human intervention assessment

**Options:**
- `--json`: Output machine-readable JSON format (for both scripts)
- `--verbose`: Show detailed progress information
