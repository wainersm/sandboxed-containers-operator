---
name: osc-user-guide
description: Provides comprehensive guidance on OpenShift Sandboxed Containers (OSC) by reading official Red Hat documentation. Use when questions involve OSC installation, KataConfig configuration, node setup, bare-metal or cloud deployments, PeerPods, confidential containers, TEE, Trustee, attestation, or troubleshooting.
---

# OSC User Guide Reader

When this skill is triggered, follow these steps to answer the user's question using the official OSC documentation:

## Instructions for Claude

1. **Determine the latest OSC version** using the WebFetch tool:
   ```
   WebFetch(url='https://docs.redhat.com/en/documentation/openshift_sandboxed_containers',
            prompt='What is the latest version of OpenShift Sandboxed Containers documentation? Return only the version number (e.g., 1.12)')
   ```

   Extract the version number from the response.

2. **Download PDFs** using the Bash tool with the discovered version:
   ```bash
   bash .claude/skills/osc-user-guide/download-pdfs.sh <version>
   ```

   For example, if the version is 1.12:
   ```bash
   bash .claude/skills/osc-user-guide/download-pdfs.sh 1.12
   ```

   This script will:
   - For 1.12+: Download all per-platform PDF guides (16 guides across 3 categories + release notes)
   - For 1.11 and earlier: Download the 3 monolithic PDF guides
   - Display the paths to the available documentation
   - No dependencies required (just curl or wget)

3. **Read the relevant PDF(s)** using Claude's built-in Read tool:

   The download script output will show the paths to the available PDFs.
   Use those paths to read the documentation.

   **How to read PDFs:**
   - Use the Read tool with the `pages` parameter
   - Maximum 20 pages per Read call
   - Example: `Read(file_path='<path_from_download_script_output>', pages='1-20')`

   **Reading strategy:**
   - Determine which PDF is most relevant to the user's question
   - Read the entire PDF to find comprehensive information
   - For most questions, reading one full PDF is sufficient
   - If needed, read additional PDFs

   **Guide selection — choose based on the user's question:**

   From **1.12+**, the docs are split per platform. Pick the guide matching the user's platform:

   **Category 1: Deploying OpenShift Sandboxed Containers**
   - On bare-metal servers — Operator install, KataConfig, kata runtime, NFD
   - On Microsoft Azure — Peer pods on Azure, networking, peer-pods-cm
   - On IBM Z and IBM LinuxONE — s390x peer pods
   - On AWS — Peer pods on AWS
   - On Google Cloud — Peer pods on GCP

   **Category 2: Deploying Confidential Containers**
   - On bare-metal servers — kata-cc runtime, Intel TDX, TEE, initdata, attestation
   - On Microsoft Azure — kata-remote runtime, Azure CoCo peer pods, SEV-SNP/TDX
   - On Microsoft Azure Red Hat OpenShift (ARO) — CoCo on managed ARO
   - On IBM Z and IBM LinuxONE with peer pods — s390x CoCo peer pods
   - On IBM Z and IBM LinuxONE bare-metal servers — s390x CoCo bare-metal

   **Category 3: Deploying Red Hat Build of Trustee**
   - For workloads on bare-metal servers — Trustee/KBS deployment, attestation
   - For workloads on bare-metal (disconnected) — Air-gapped Trustee
   - For workloads on Microsoft Azure — Trustee for Azure CoCo
   - For workloads on IBM Z and IBM LinuxONE — Trustee for s390x

   **Release Notes** — New features, bug fixes, known issues

   For **1.11 and earlier**, the docs are 3 monolithic PDFs:
   1. Deploying Red Hat OpenShift Sandboxed Containers (all platforms)
   2. Deploying Confidential Containers (all platforms)
   3. Deploying Red Hat Build of Trustee

   If the user doesn't specify a platform, default to bare-metal. If unsure which guide, read the most relevant one first — it's usually enough.

4. **Answer the question comprehensively:**
   - Provide a direct answer to the user's question
   - Include step-by-step instructions when applicable
   - Show code examples and YAML configurations
   - List prerequisites and requirements
   - Cite which guide(s) and page numbers the information comes from
   - Mention related topics the user should know about

## How This Skill Works

This skill is **automatically triggered** by Claude when you ask questions about OpenShift Sandboxed Containers. You don't need to explicitly invoke it - just ask your question naturally.

When triggered, the skill:
1. Fetches the latest OSC documentation version from Red Hat docs
2. Downloads PDFs for that version if needed (first run only; ~4 MB for 1.12+, ~1.7 MB for 1.11)
3. Claude reads the relevant PDF(s) using the built-in Read tool
4. Claude provides a comprehensive answer with examples and citations

## Example Questions That Trigger This Skill

Ask questions naturally - the skill will activate automatically:

**General deployment:**
- "How do I install the OSC operator?"
- "Show me KataConfig configuration options"
- "How do I deploy OSC on a subset of worker nodes?"
- "What are the node eligibility requirements?"

**Confidential containers:**
- "How do I deploy confidential containers?"
- "What hardware is required for TEE?"
- "How does attestation work in confidential containers?"

**Trustee:**
- "How do I configure Red Hat build of Trustee?"
- "How do I create attestation tokens?"
- "What is the key broker service?"

**Troubleshooting:**
- "Why is my KataConfig failing?"
- "How do I verify Kata runtime installation?"

## Requirements

- `curl` or `wget` for downloading PDFs
- Internet connection (for initial download only)
- Read access to .claude/skills directory

## Setup for Team Members

**No manual setup required!**

The first time you run this skill:
1. Automatically detects the latest OSC documentation version
2. Downloads all OSC User Guide PDFs for that version:
   - **1.12+**: 16 per-platform guides + release notes (~4 MB total)
   - **1.11 and earlier**: 3 monolithic guides (~1.7 MB total)

On subsequent runs, it uses the cached PDFs (unless a new version is detected).

