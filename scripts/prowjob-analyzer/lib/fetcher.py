"""
Artifact Fetcher Module

Handles URL parsing and fetching artifacts from Prow/GCS.
"""

import re
import time
import json
import logging
from typing import Dict, Optional, Tuple, List
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)


def parse_prow_url(url: str) -> Tuple[str, str, str]:
    """
    Parse a Prow job URL to extract job name and build ID.
    Supports both periodic and presubmit (PR rehearsal) job URLs.

    Args:
        url: Prow UI URL (https://prow.ci.openshift.org/view/gs/...)

    Returns:
        Tuple of (base_url, job_name, build_id)

    Raises:
        ValueError: If URL format is invalid
    """
    # Try presubmit/PR pattern first (more specific)
    # Format: https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/{ORG}_{REPO}/{PR_NUMBER}/{JOB_NAME}/{BUILD_ID}
    pr_pattern = r'https://prow\.ci\.openshift\.org/view/gs/([^/]+)/pr-logs/pull/([^/]+)/([^/]+)/([^/]+)/([^/\?]+)'
    match = re.match(pr_pattern, url)

    if match:
        bucket = match.group(1)
        org_repo = match.group(2)
        pr_number = match.group(3)
        job_name = match.group(4)
        build_id = match.group(5)

        # Construct base URL for presubmit jobs
        base_url = f"https://prow.ci.openshift.org/view/gs/{bucket}/pr-logs/pull/{org_repo}/{pr_number}/{job_name}/{build_id}"
        logger.debug(f"Parsed as presubmit job: PR {org_repo}#{pr_number}")
        return base_url, job_name, build_id

    # Try periodic/postsubmit pattern
    # Format: https://prow.ci.openshift.org/view/gs/test-platform-results/logs/{JOB_NAME}/{BUILD_ID}
    periodic_pattern = r'https://prow\.ci\.openshift\.org/view/gs/([^/]+)/([^/]+)/([^/]+)/([^/\?]+)'
    match = re.match(periodic_pattern, url)

    if match:
        bucket = match.group(1)
        log_type = match.group(2)
        job_name = match.group(3)
        build_id = match.group(4)

        # Construct base URL for periodic/postsubmit jobs
        base_url = f"https://prow.ci.openshift.org/view/gs/{bucket}/{log_type}/{job_name}/{build_id}"
        logger.debug(f"Parsed as periodic/postsubmit job")
        return base_url, job_name, build_id

    # No pattern matched
    raise ValueError(
        f"Invalid Prow URL format. Expected one of:\n"
        f"  Periodic: https://prow.ci.openshift.org/view/gs/test-platform-results/logs/{{JOB_NAME}}/{{BUILD_ID}}\n"
        f"  Presubmit: https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/{{ORG}}_{{REPO}}/{{PR}}/{{JOB_NAME}}/{{BUILD_ID}}\n"
        f"Got: {url}"
    )


def extract_variant_from_job_name(job_name: str) -> Optional[str]:
    """
    Extract the variant from job name for artifact path construction.

    For OSC jobs, the variant is typically: {provider}-ipi-{workload}
    Example: periodic-ci-openshift-sandboxed-containers-operator-devel-downstream-candidate-aws-ipi-peerpods
    Variant: aws-ipi-peerpods

    Args:
        job_name: Prow job name

    Returns:
        Variant string or None if not found
    """
    # Look for known patterns in OSC job names
    # Pattern: ...downstream-candidate-{VARIANT}
    pattern = r'downstream-candidate-(.+)$'
    match = re.search(pattern, job_name)

    if match:
        return match.group(1)

    # Try alternative patterns for other job types
    # Pattern: ...{provider}-ipi-{workload}
    providers = ['aws', 'azure', 'gcp', 'ibmcloud', 'vsphere']
    for provider in providers:
        pattern = f'({provider}-ipi-[^-]+)'
        match = re.search(pattern, job_name)
        if match:
            return match.group(1)

    logger.warning(f"Could not extract variant from job name: {job_name}")
    return None


def discover_gcs_url_from_prow(prow_url: str) -> Optional[str]:
    """
    Discover the actual GCS web URL by parsing Prow's HTML response.

    Args:
        prow_url: Prow view URL that may return HTML

    Returns:
        Discovered GCS web URL, or None if not found
    """
    try:
        req = Request(prow_url, headers={'User-Agent': 'prowjob-analyzer/1.0'})
        with urlopen(req, timeout=30) as response:
            content_type = response.headers.get('Content-Type', '')

            if 'text/html' in content_type:
                # Parse HTML to extract GCS web URL
                html = response.read().decode('utf-8', errors='ignore')
                # Look for gcsweb URL in the HTML
                match = re.search(r'https://[^"\s]*gcsweb[^"\s]*', html)
                if match:
                    gcs_url = match.group(0).rstrip('/')
                    logger.debug(f"Discovered GCS URL: {gcs_url}")
                    return gcs_url

    except Exception as e:
        logger.debug(f"Failed to discover GCS URL from {prow_url}: {e}")

    return None


def fetch_artifact(base_url: str, artifact_path: str, max_retries: int = 3) -> Optional[bytes]:
    """
    Fetch an artifact from Prow/GCS with retry logic.
    Dynamically discovers the GCS web URL if Prow returns HTML.

    Args:
        base_url: Base URL of the Prow job
        artifact_path: Relative path to the artifact (e.g., "prowjob.json")
        max_retries: Maximum number of retry attempts

    Returns:
        Artifact content as bytes, or None if not found
    """
    url = f"{base_url}/{artifact_path}"

    for attempt in range(max_retries):
        try:
            logger.debug(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            req = Request(url, headers={'User-Agent': 'prowjob-analyzer/1.0'})

            with urlopen(req, timeout=30) as response:
                content_type = response.headers.get('Content-Type', '')
                content = response.read()

                # Check if we got HTML instead of the actual artifact
                if 'text/html' in content_type and attempt == 0:
                    logger.debug(f"Got HTML response, discovering GCS URL...")
                    # Try to discover the actual GCS URL from the HTML
                    gcs_url = discover_gcs_url_from_prow(url)
                    if gcs_url:
                        # Retry with the discovered GCS URL
                        logger.debug(f"Retrying with discovered GCS URL: {gcs_url}")
                        req = Request(gcs_url, headers={'User-Agent': 'prowjob-analyzer/1.0'})
                        with urlopen(req, timeout=30) as gcs_response:
                            content = gcs_response.read()
                            logger.debug(f"Successfully fetched from GCS ({len(content)} bytes)")
                            return content

                logger.debug(f"Successfully fetched {url} ({len(content)} bytes)")
                return content

        except HTTPError as e:
            if e.code == 404:
                logger.debug(f"Artifact not found: {url}")
                return None
            elif e.code in (500, 502, 503, 504) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Server error {e.code}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error fetching {url}: {e.code} {e.reason}")
                return None

        except URLError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Network error, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url}: {e}")
                return None

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    return None


def fetch_json_artifact(base_url: str, artifact_path: str) -> Optional[Dict]:
    """
    Fetch and parse a JSON artifact.

    Args:
        base_url: Base URL of the Prow job
        artifact_path: Relative path to the JSON artifact

    Returns:
        Parsed JSON as dict, or None if not found or invalid
    """
    content = fetch_artifact(base_url, artifact_path)
    if content is None:
        return None

    try:
        return json.loads(content.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Failed to parse JSON from {artifact_path}: {e}")
        return None


def check_artifacts_ready(base_url: str) -> bool:
    """
    Check if job artifacts are ready (job has finished).

    Args:
        base_url: Base URL of the Prow job

    Returns:
        True if artifacts are ready, False otherwise
    """
    # Check for finished.json which indicates the job has completed
    finished = fetch_json_artifact(base_url, "finished.json")
    return finished is not None


def wait_for_artifacts(base_url: str, timeout: int = 300, poll_interval: int = 10) -> bool:
    """
    Wait for job artifacts to become available.

    Args:
        base_url: Base URL of the Prow job
        timeout: Maximum time to wait in seconds (default: 5 minutes)
        poll_interval: Time between polls in seconds (default: 10 seconds)

    Returns:
        True if artifacts became ready, False if timeout
    """
    start_time = time.time()

    logger.info(f"Waiting for job artifacts (timeout: {timeout}s)...")

    while (time.time() - start_time) < timeout:
        if check_artifacts_ready(base_url):
            elapsed = time.time() - start_time
            logger.info(f"Artifacts ready after {elapsed:.1f}s")
            return True

        remaining = timeout - (time.time() - start_time)
        logger.info(f"Job still running, checking again in {poll_interval}s (timeout in {remaining:.0f}s)...")
        time.sleep(poll_interval)

    logger.warning(f"Timeout waiting for artifacts after {timeout}s")
    return False


def get_artifact_url(base_url: str, artifact_path: str) -> str:
    """
    Generate a GCS web URL for an artifact.

    Args:
        base_url: Base URL of the Prow job
        artifact_path: Relative path to the artifact

    Returns:
        Full URL to the artifact
    """
    return f"{base_url}/{artifact_path}"


def get_step_directories(base_url: str, variant: str) -> List[str]:
    """
    Get list of step directories from artifacts.

    Args:
        base_url: Base URL of the Prow job
        variant: Job variant (e.g., "aws-ipi-peerpods")

    Returns:
        List of step directory names
    """
    artifacts_url = f"{base_url}/artifacts/{variant}/"

    try:
        req = Request(artifacts_url, headers={'User-Agent': 'prowjob-analyzer/1.0'})
        with urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8', errors='ignore')

            # Extract directory names from HTML listing
            # Look for patterns like: href="step-name/"
            pattern = r'href="([a-z0-9-]+)/"'
            matches = re.findall(pattern, html_content)

            # Filter out parent directory references and common non-step directories
            step_dirs = [
                m for m in matches
                if m not in ['..', 'artifacts'] and not m.startswith('/')
            ]

            logger.debug(f"Found {len(step_dirs)} step directories in {variant}")
            return step_dirs

    except Exception as e:
        logger.warning(f"Failed to get step directories: {e}")
        return []


def get_failed_steps(base_url: str, variant: str) -> List[str]:
    """
    Identify which steps failed by checking their finished.json files.

    Args:
        base_url: Base URL of the Prow job
        variant: Job variant (e.g., "aws-ipi-peerpods")

    Returns:
        List of failed step names
    """
    step_dirs = get_step_directories(base_url, variant)
    failed_steps = []

    for step in step_dirs:
        finished_path = f"artifacts/{variant}/{step}/finished.json"
        finished_data = fetch_json_artifact(base_url, finished_path)

        if finished_data:
            # Check if step failed
            passed = finished_data.get('passed', True)
            result = finished_data.get('result', '').upper()

            if not passed or result == 'FAILURE':
                failed_steps.append(step)
                logger.debug(f"Step {step} failed: passed={passed}, result={result}")

    logger.debug(f"Found {len(failed_steps)} failed steps: {failed_steps}")
    return failed_steps
