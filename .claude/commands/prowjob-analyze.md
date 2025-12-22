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
2. Based on which step failed, decide if further analysis is needed

Execute the following steps:

**Step 1: Run main analyzer**
```bash
python3 scripts/prowjob-analyzer/analyze.py --no-wait "$@"
```

**Step 2: Analyze the output**
- Review the analysis report from Step 1
- Check the "Failure Analysis" section to see which step(s) failed
- Check if there are "Failed Tests" listed

**Step 3: Determine next action based on failed step**

**Case A: Tests failed** (Failed Step is `openshift-extended-test` AND Failed Tests are listed)
- This means the job ran through infrastructure setup and failed during test execution
- Run detailed test analysis:
```bash
python3 scripts/prowjob-analyzer/test_report.py <PROW_JOB_URL> <TEST_NAME_1> <TEST_NAME_2> ...
```
Use the exact test names from the "Failed Tests" section.

**Case B: Infrastructure/setup step failed** (Failed Step is NOT `openshift-extended-test`)
- Examples: `ipi-install-install`, `sandboxed-containers-operator-peerpods-param-cm`, etc.
- This means tests never ran - job failed before reaching the test step
- Do NOT run test_report.py
- Provide summary explaining that the job failed at infrastructure/setup stage
- Point user to the specific step's artifacts for investigation

**Case C: Multiple steps failed**
- If `openshift-extended-test` is among the failed steps AND has failing tests, run test analysis
- Otherwise, treat as Case B

---

## About

Comprehensive Prow job analysis with two-level investigation:

**Level 1: Overall Analysis** (analyze.py)
- Extracts job metadata (provider, OCP version, Kata RPM, catalog, etc.)
- Determines overall job status (pass/fail/timeout)
- Identifies which step(s) failed
- Lists failing tests if tests ran and failed
- Provides links to all artifacts

**Level 2: Detailed Test Debugging** (test_report.py - only when tests failed)
- Only runs if `openshift-extended-test` step failed with failing tests
- Extracts error messages from build logs for each failing test
- Provides log context around each failure
- Detects test-specific patterns (timeout, OOM, network, etc.)
- Offers debugging hints based on detected patterns

**Important:** If the job failed at an earlier step (like `ipi-install-install`),
tests never ran and test analysis is not applicable. The analyzer will correctly
identify which infrastructure/setup step failed.

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
- Identifies which step(s) failed
- For test failures: Detailed debugging information for each failing test
- For infrastructure failures: Guidance on which step failed and where to investigate
- Links to all relevant artifacts

**Options:**
- `--json`: Output machine-readable JSON format (for both scripts)
- `--verbose`: Show detailed progress information
